"""
Whitepaper analysis utilities for extracting insights from financial and technical whitepapers.

This module provides functionality for:
- Loading and preprocessing whitepaper text
- Extracting key topics and concepts
- Sentiment analysis of whitepaper content
- Identifying relevant companies and technologies
- Assessing market potential and innovation factors
"""

import asyncio
import json
import logging
import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import aiohttp
import nltk
import numpy as np
import pandas as pd
from gensim import corpora
from gensim.models import LdaModel
from gensim.utils import simple_preprocess
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer

from models.finbert_sentiment import FinBertSentiment

logger = logging.getLogger("api")

# Download required NLTK resources
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except Exception as e:
    logger.warning(f"Failed to download NLTK resources: {e}")


class WhitepaperAnalyzer:
    """Analyzer for financial and technical whitepapers."""
    
    def __init__(self, cache_dir: str = "cache/whitepapers"):
        """
        Initialize whitepaper analyzer.
        
        Args:
            cache_dir: Directory for caching processed whitepapers
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.finbert = FinBertSentiment()
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Add finance-specific stop words
        self.finance_stop_words = {
            'company', 'market', 'financial', 'investment', 'investor', 'stock',
            'share', 'value', 'price', 'report', 'quarterly', 'annual', 'year',
            'month', 'percent', 'growth', 'increase', 'decrease', 'page', 'technology',
            'solution', 'business', 'may', 'could', 'would', 'also', 'include', 'provide'
        }
        self.stop_words.update(self.finance_stop_words)
        
        # Financial and technology entity lists
        self._load_entity_lists()
        
        # Technical terms dictionary for mapping jargon to explanations
        self._load_technical_terms()
    
    def _load_entity_lists(self) -> None:
        """Load lists of companies, technologies, and financial terms."""
        # In a real implementation, these would be loaded from comprehensive files
        # For this example, using small sample lists
        self.company_names = {
            'apple', 'google', 'microsoft', 'amazon', 'facebook', 'meta',
            'tesla', 'nvidia', 'amd', 'intel', 'ibm', 'oracle', 'salesforce',
            'jpmorgan', 'goldman sachs', 'morgan stanley', 'bank of america',
            'citigroup', 'wells fargo', 'blackrock', 'vanguard', 'fidelity'
        }
        
        self.tech_terms = {
            'artificial intelligence', 'machine learning', 'deep learning', 'neural network',
            'blockchain', 'cryptocurrency', 'bitcoin', 'ethereum', 'distributed ledger',
            'cloud computing', 'quantum computing', 'big data', 'data science',
            'fintech', 'regtech', 'insurtech', 'robo-advisor', 'algorithmic trading',
            'high frequency trading', 'natural language processing', 'computer vision'
        }
        
        self.financial_terms = {
            'stock', 'bond', 'equity', 'dividend', 'yield', 'portfolio', 'asset',
            'liability', 'balance sheet', 'income statement', 'cash flow', 'profit',
            'revenue', 'ebitda', 'pe ratio', 'eps', 'market cap', 'liquidity',
            'volatility', 'derivative', 'option', 'futures', 'hedge fund', 'etf'
        }
    
    def _load_technical_terms(self) -> None:
        """Load dictionary of technical terms and their explanations."""
        # In a real implementation, this would be loaded from a comprehensive file
        # For this example, using a small sample dictionary
        self.technical_terms_dict = {
            'blockchain': 'A distributed ledger technology that maintains a growing list of records (blocks) linked using cryptography.',
            'machine learning': 'A field of AI that uses statistical techniques to give computers the ability to learn from data.',
            'neural network': 'A computing system inspired by biological neural networks that can learn from observational data.',
            'etf': 'Exchange-Traded Fund, an investment fund traded on stock exchanges that holds assets such as stocks or bonds.',
            'volatility': 'A statistical measure of the dispersion of returns for a given security or market index.',
            'algo trading': 'The use of computer algorithms to automatically make trading decisions, submit orders, and manage those orders.',
            'liquidity': 'The degree to which an asset can be quickly bought or sold without affecting its price.',
            'smart contract': 'Self-executing contracts with the terms directly written into code, typically on a blockchain platform.',
            'defi': 'Decentralized Finance, blockchain-based financial services that operate without centralized intermediaries.',
            'nft': 'Non-Fungible Token, a unique digital identifier recorded on a blockchain to certify authenticity and ownership.'
        }
        
    async def analyze_whitepaper(self, file_path: str, paper_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a whitepaper file.
        
        Args:
            file_path: Path to whitepaper file (PDF or text)
            paper_id: Unique identifier for the whitepaper
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Extract ID from file path if not provided
            if not paper_id:
                paper_id = os.path.basename(file_path).split('.')[0]
            
            # Check cache first
            cache_result = self._check_cache(paper_id)
            if cache_result:
                return cache_result
            
            # Extract text from whitepaper
            text = await self._extract_text(file_path)
            if not text:
                return {"error": f"Failed to extract text from {file_path}"}
            
            # Pre-process text
            processed_text = self._preprocess_text(text)
            
            # Initialize results dictionary
            results = {
                "paper_id": paper_id,
                "filename": os.path.basename(file_path),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "text_length": len(text),
                "word_count": len(text.split()),
                "sentence_count": len(sent_tokenize(text))
            }
            
            # Perform various analyses
            results["key_topics"] = self._extract_topics(processed_text)
            results["key_phrases"] = self._extract_key_phrases(text)
            results["sentiment_analysis"] = await self._analyze_sentiment(text)
            results["entities"] = self._extract_entities(text)
            results["complexity_metrics"] = self._calculate_complexity(text)
            results["innovation_score"] = self._calculate_innovation_score(
                results["key_topics"], 
                results["entities"]
            )
            results["market_potential"] = self._assess_market_potential(
                results["key_topics"],
                results["entities"],
                results["sentiment_analysis"]
            )
            results["summary"] = self._generate_summary(results)
            
            # Cache results
            self._cache_results(paper_id, results)
            
            return results
        
        except Exception as e:
            logger.exception(f"Error analyzing whitepaper: {e}")
            return {
                "paper_id": paper_id if paper_id else "unknown",
                "filename": os.path.basename(file_path),
                "error": str(e),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
    
    async def compare_whitepapers(
        self, file_paths: List[str], ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare multiple whitepapers.
        
        Args:
            file_paths: List of paths to whitepaper files
            ids: List of whitepaper IDs
            
        Returns:
            Dictionary with comparison results
        """
        try:
            if not ids:
                ids = [os.path.basename(path).split('.')[0] for path in file_paths]
            
            if len(file_paths) != len(ids):
                return {"error": "Number of file paths must match number of IDs"}
            
            # Analyze each whitepaper
            analyses = []
            for i, file_path in enumerate(file_paths):
                analysis = await self.analyze_whitepaper(file_path, ids[i])
                analyses.append(analysis)
            
            # Compare topics across papers
            common_topics = self._find_common_topics(analyses)
            topic_similarity = self._calculate_topic_similarity(analyses)
            
            # Compare entities across papers
            common_entities = self._find_common_entities(analyses)
            
            # Compare sentiment across papers
            sentiment_comparison = self._compare_sentiment(analyses)
            
            # Compare innovation and market potential
            innovation_comparison = {
                paper["paper_id"]: paper.get("innovation_score", 0) 
                for paper in analyses
            }
            
            market_potential_comparison = {
                paper["paper_id"]: paper.get("market_potential", {}).get("overall_score", 0) 
                for paper in analyses
            }
            
            # Generate comparative summary
            comparative_summary = self._generate_comparative_summary(
                analyses, common_topics, topic_similarity, 
                innovation_comparison, market_potential_comparison
            )
            
            return {
                "papers_analyzed": len(analyses),
                "paper_ids": ids,
                "common_topics": common_topics,
                "topic_similarity_matrix": topic_similarity,
                "common_entities": common_entities,
                "sentiment_comparison": sentiment_comparison,
                "innovation_comparison": innovation_comparison,
                "market_potential_comparison": market_potential_comparison,
                "comparative_summary": comparative_summary,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.exception(f"Error comparing whitepapers: {e}")
            return {
                "error": str(e),
                "papers_analyzed": 0,
                "paper_ids": ids if ids else [],
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
    
    def extract_investment_insights(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract investment insights from whitepaper analysis.
        
        Args:
            analysis: Whitepaper analysis results
            
        Returns:
            Dictionary with investment insights
        """
        try:
            if "error" in analysis:
                return {"error": analysis["error"]}
            
            # Extract key topics and entities
            key_topics = analysis.get("key_topics", {}).get("topics", [])
            key_entities = analysis.get("entities", {})
            companies = key_entities.get("companies", [])
            technologies = key_entities.get("technologies", [])
            
            # Extract sentiment
            sentiment = analysis.get("sentiment_analysis", {})
            overall_sentiment = sentiment.get("overall_sentiment", "neutral")
            
            # Identify potential investment sectors
            sectors = self._identify_sectors(key_topics, technologies)
            
            # Identify relevant companies
            public_companies = self._filter_public_companies(companies)
            private_companies = [c for c in companies if c not in public_companies]
            
            # Assess technology maturity
            tech_maturity = self._assess_technology_maturity(technologies, key_topics)
            
            # Assess market growth potential
            market_potential = analysis.get("market_potential", {})
            growth_potential = market_potential.get("growth_potential", "medium")
            
            # Generate investment thesis
            investment_thesis = self._generate_investment_thesis(
                key_topics, sectors, companies, technologies, 
                overall_sentiment, growth_potential
            )
            
            # Identify risks
            risks = self._identify_risks(analysis)
            
            return {
                "paper_id": analysis.get("paper_id", "unknown"),
                "investment_sectors": sectors,
                "public_companies": public_companies,
                "private_companies": private_companies,
                "key_technologies": technologies[:5] if len(technologies) > 5 else technologies,
                "technology_maturity": tech_maturity,
                "market_growth_potential": growth_potential,
                "sentiment": overall_sentiment,
                "investment_thesis": investment_thesis,
                "risk_factors": risks,
                "confidence_score": self._calculate_confidence(analysis),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.exception(f"Error extracting investment insights: {e}")
            return {
                "error": str(e),
                "paper_id": analysis.get("paper_id", "unknown"),
                "generated_at": datetime.utcnow().isoformat()
            }
    
    async def _extract_text(self, file_path: str) -> str:
        """
        Extract text from a whitepaper file.
        
        Args:
            file_path: Path to whitepaper file
            
        Returns:
            Extracted text
        """
        try:
            # Check file extension
            ext = file_path.split('.')[-1].lower()
            
            if ext == 'pdf':
                # In a real implementation, use a library like PyPDF2 or pdfminer
                # For this example, simulate PDF extraction
                return await self._simulate_pdf_extraction(file_path)
            
            elif ext == 'txt':
                # Read text file
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            else:
                logger.warning(f"Unsupported file extension: {ext}")
                return ""
            
        except Exception as e:
            logger.exception(f"Error extracting text from {file_path}: {e}")
            return ""
    
    async def _simulate_pdf_extraction(self, file_path: str) -> str:
        """
        Simulate PDF text extraction for demo purposes.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text (simulated)
        """
        try:
            # In a real implementation, use a proper PDF extraction library
            # For example: PyPDF2, pdfminer, or pdfplumber
            
            # For simulation, check if the file exists
            if not os.path.exists(file_path):
                return f"Error: File not found at {file_path}"
            
            # Generate simulated content based on filename
            filename = os.path.basename(file_path)
            base_name = filename.split('.')[0].lower()
            
            # Generate placeholder text
            if 'blockchain' in base_name:
                return self._generate_blockchain_whitepaper_text()
            elif 'ai' in base_name or 'ml' in base_name:
                return self._generate_ai_whitepaper_text()
            elif 'fintech' in base_name:
                return self._generate_fintech_whitepaper_text()
            else:
                return self._generate_generic_tech_whitepaper_text()
                
        except Exception as e:
            logger.exception(f"Error in simulated PDF extraction: {e}")
            return ""
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess whitepaper text for analysis.
        
        Args:
            text: Raw text
            
        Returns:
            Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\d+', ' ', text)
        
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_topics(self, text: str) -> Dict[str, Any]:
        """
        Extract key topics from whitepaper text.
        
        Args:
            text: Preprocessed text
            
        Returns:
            Dictionary with topic modeling results
        """
        try:
            # Tokenize and remove stop words
            tokens = [
                word for word in word_tokenize(text)
                if word not in self.stop_words and len(word) > 3
            ]
            
            # Lemmatize tokens
            lemmatized_tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
            
            # Create document for LDA
            processed_doc = ' '.join(lemmatized_tokens)
            
            # Use TF-IDF and NMF for topic extraction (simplified for demonstration)
            vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                max_df=0.9,
                min_df=0.1
            )
            
            # Create document-term matrix
            tfidf_matrix = vectorizer.fit_transform([processed_doc])
            feature_names = vectorizer.get_feature_names_out()
            
            # Extract topics using NMF
            num_topics = 5
            nmf_model = NMF(n_components=num_topics, random_state=42)
            nmf_model.fit(tfidf_matrix)
            
            # Get top words for each topic
            topics = []
            for topic_idx, topic in enumerate(nmf_model.components_):
                top_words_idx = topic.argsort()[:-11:-1]
                top_words = [feature_names[i] for i in top_words_idx]
                
                # Generate topic name based on top words
                topic_name = self._generate_topic_name(top_words)
                
                topics.append({
                    "id": topic_idx,
                    "name": topic_name,
                    "top_words": top_words,
                    "weight": float(topic.sum() / nmf_model.components_.sum())
                })
            
            return {
                "topics": topics,
                "methodology": "NMF",
                "num_topics": num_topics
            }
            
        except Exception as e:
            logger.exception(f"Error extracting topics: {e}")
            return {
                "topics": [],
                "error": str(e)
            }
    
    def _generate_topic_name(self, top_words: List[str]) -> str:
        """
        Generate a descriptive name for a topic based on its top words.
        
        Args:
            top_words: List of top words for the topic
            
        Returns:
            Generated topic name
        """
        # Check for specific technology patterns
        tech_patterns = {
            'blockchain': ['blockchain', 'crypto', 'token', 'defi', 'decentralized', 'ledger', 'bitcoin', 'ethereum'],
            'ai': ['ai', 'machine', 'learning', 'neural', 'algorithm', 'intelligence', 'model', 'prediction'],
            'cloud': ['cloud', 'saas', 'service', 'platform', 'infrastructure', 'hosted', 'server'],
            'fintech': ['banking', 'payment', 'transaction', 'financial', 'finance', 'loan', 'credit'],
            'security': ['security', 'encryption', 'privacy', 'protection', 'cyber', 'attack', 'threat']
        }
        
        # Check if top words match any technology pattern
        for tech_name, tech_words in tech_patterns.items():
            matches = sum(1 for word in top_words if word in tech_words)
            if matches >= 2:  # At least 2 matching words
                return f"{tech_name.title()} Technology"
        
        # If no specific pattern matched, use first two words
        return ' '.join(w.title() for w in top_words[:2])
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """
        Extract important phrases from whitepaper.
        
        Args:
            text: Raw whitepaper text
            
        Returns:
            List of key phrases
        """
        try:
            # Split into sentences
            sentences = sent_tokenize(text)
            
            # Score sentences based on word frequency
            word_freq = Counter()
            for sentence in sentences:
                words = word_tokenize(sentence.lower())
                words = [
                    word for word in words 
                    if word not in self.stop_words and len(word) > 2 and word.isalnum()
                ]
                word_freq.update(words)
            
            # Score each sentence
            sentence_scores = []
            for sentence in sentences:
                if len(sentence.split()) < 5 or len(sentence.split()) > 25:
                    continue  # Skip very short or long sentences
                
                score = 0
                words = word_tokenize(sentence.lower())
                for word in words:
                    if word in word_freq:
                        score += word_freq[word]
                
                sentence_scores.append((sentence, score))
            
            # Get top phrases based on scores
            top_phrases = [s[0] for s in sorted(sentence_scores, key=lambda x: x[1], reverse=True)[:10]]
            
            return top_phrases
            
        except Exception as e:
            logger.exception(f"Error extracting key phrases: {e}")
            return []
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of whitepaper text.
        
        Args:
            text: Whitepaper text
            
        Returns:
            Dictionary with sentiment analysis results
        """
        try:
            # Split into sections for analysis
            sections = []
            
            # Extract abstract/introduction (first 1000 characters)
            intro = text[:1000]
            sections.append(("introduction", intro))
            
            # Extract conclusion (last 1000 characters)
            conclusion = text[-1000:]
            sections.append(("conclusion", conclusion))
            
            # Extract some sections from the middle
            mid_point = len(text) // 2
            middle_text = text[mid_point-500:mid_point+500]
            sections.append(("middle", middle_text))
            
            # Create sentences for sentiment analysis
            sentences = []
            for section_name, section_text in sections:
                section_sentences = sent_tokenize(section_text)
                # Take up to 5 sentences from each section
                for i, sentence in enumerate(section_sentences[:5]):
                    if len(sentence.split()) > 5:  # Only include sentences with at least 5 words
                        sentences.append(sentence)
            
            # Use FinBERT for sentiment analysis
            sentiment_results = self.finbert.predict(sentences)
            
            # Analyze overall sentiment
            sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
            for result in sentiment_results:
                sentiment = result.get("sentiment", "neutral")
                sentiment_counts[sentiment] += 1
            
            # Determine overall sentiment
            total = sum(sentiment_counts.values()) or 1  # Avoid division by zero
            overall_sentiment = max(sentiment_counts, key=sentiment_counts.get)
            
            # Calculate sentiment score (-100 to +100)
            sentiment_score = int(
                ((sentiment_counts["positive"] - sentiment_counts["negative"]) / total) * 100
            )
            
            return {
                "overall_sentiment": overall_sentiment,
                "sentiment_score": sentiment_score,
                "distribution": {
                    "positive": round(sentiment_counts["positive"] / total * 100, 1),
                    "neutral": round(sentiment_counts["neutral"] / total * 100, 1),
                    "negative": round(sentiment_counts["negative"] / total * 100, 1)
                },
                "section_analysis": {
                    section_name: self._get_section_sentiment(
                        [r for i, r in enumerate(sentiment_results) if i < len(sentences)]
                    )
                    for section_name, _ in sections
                }
            }
            
        except Exception as e:
            logger.exception(f"Error analyzing sentiment: {e}")
            return {
                "overall_sentiment": "neutral",
                "error": str(e)
            }
    
    def _get_section_sentiment(self, results: List[Dict[str, Any]]) -> str:
        """
        Get dominant sentiment for a section.
        
        Args:
            results: Sentiment analysis results for section
            
        Returns:
            Dominant sentiment
        """
        if not results:
            return "neutral"
        
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        for result in results:
            sentiment = result.get("sentiment", "neutral")
            sentiment_counts[sentiment] += 1
        
        return max(sentiment_counts, key=sentiment_counts.get)
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract relevant entities from whitepaper.
        
        Args:
            text: Whitepaper text
            
        Returns:
            Dictionary with extracted entities
        """
        try:
            text_lower = text.lower()
            
            # Extract companies
            companies = []
            for company in self.company_names:
                if company in text_lower:
                    companies.append(company)
            
            # Extract technologies
            technologies = []
            for tech in self.tech_terms:
                if tech in text_lower:
                    technologies.append(tech)
            
            # Extract financial terms
            financial_terms = []
            for term in self.financial_terms:
                if term in text_lower:
                    financial_terms.append(term)
            
            # Extract references to regulatory bodies or standards
            regulatory_bodies = []
            regulators = ['sec', 'finra', 'fdic', 'occ', 'cftc', 'federal reserve',
                        'fca', 'esma', 'bafin', 'iso', 'nist', 'gdpr']
            
            for regulator in regulators:
                if regulator in text_lower:
                    regulatory_bodies.append(regulator)
            
            return {
                "companies": companies,
                "technologies": technologies,
                "financial_terms": financial_terms,
                "regulatory_bodies": regulatory_bodies
            }
            
        except Exception as e:
            logger.exception(f"Error extracting entities: {e}")
            return {
                "companies": [],
                "technologies": [],
                "financial_terms": [],
                "regulatory_bodies": []
            }
    
    def _calculate_complexity(self, text: str) -> Dict[str, Any]:
        """
        Calculate text complexity metrics.
        
        Args:
            text: Whitepaper text
            
        Returns:
            Dictionary with complexity metrics
        """
        try:
            # Tokenize into sentences and words
            sentences = sent_tokenize(text)
            words = word_tokenize(text)
            
            # Filter out non-words
            words = [word for word in words if word.isalnum()]
            
            # Calculate average word length
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            
            # Calculate average sentence length
            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            
            # Calculate lexical diversity (unique words / total words)
            lexical_diversity = len(set(words)) / len(words) if words else 0
            
            # Calculate approximate reading level (Flesch Reading Ease)
            # Higher score = easier to read (90-100 = 5th grade, 0-30 = college graduate)
            syllables = self._count_syllables(words)
            if len(words) > 0 and len(sentences) > 0:
                flesch_reading_ease = 206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (syllables / len(words))
                flesch_reading_ease = max(0, min(100, flesch_reading_ease))  # Clamp to 0-100
            else:
                flesch_reading_ease = 50  # Default value
            
            # Determine reading level
            if flesch_reading_ease >= 90:
                reading_level = "Very Easy"
            elif flesch_reading_ease >= 80:
                reading_level = "Easy"
            elif flesch_reading_ease >= 70:
                reading_level = "Fairly Easy"
            elif flesch_reading_ease >= 60:
                reading_level = "Standard"
            elif flesch_reading_ease >= 50:
                reading_level = "Fairly Difficult"
            elif flesch_reading_ease >= 30:
                reading_level = "Difficult"
            else:
                reading_level = "Very Difficult"
            
            return {
                "avg_word_length": round(avg_word_length, 2),
                "avg_sentence_length": round(avg_sentence_length, 2),
                "lexical_diversity": round(lexical_diversity, 3),
                "flesch_reading_ease": round(flesch_reading_ease, 1),
                "reading_level": reading_level
            }
            
        except Exception as e:
            logger.exception(f"Error calculating complexity: {e}")
            return {
                "error": str(e)
            }
    
    def _count_syllables(self, words: List[str]) -> int:
        """
        Count total syllables in word list (approximate method).
        
        Args:
            words: List of words
            
        Returns:
            Approximate syllable count
        """
        vowels = "aeiouy"
        syllable_count = 0
        
        for word in words:
            word = word.lower()
            count = 0
            
            # Handle special cases
            if len(word) <= 3:
                syllable_count += 1
                continue
            
            # Count vowel groups
            prev_is_vowel = False
            for char in word:
                is_vowel = char in vowels
                if is_vowel and not prev_is_vowel:
                    count += 1
                prev_is_vowel = is_vowel
            
            # Adjust for common patterns
            if word.endswith('e'):
                count -= 1
            if word.endswith('le'):
                count += 1
            if word.endswith('y'):
                count += 1
            if count == 0:
                count = 1
            
            syllable_count += count
        
        return syllable_count
    
    def _calculate_innovation_score(
        self, topics: Dict[str, Any], entities: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Calculate innovation score based on topics and entities.
        
        Args:
            topics: Topic analysis results
            entities: Extracted entities
            
        Returns:
            Dictionary with innovation assessment
        """
        try:
            # Extract technologies
            technologies = entities.get("technologies", [])
            
            # Base innovation score
            base_score = 50
            
            # Add points for emerging technologies
            emerging_techs = ['quantum computing', 'blockchain', 'ai', 'machine learning',
                            'deep learning', 'neural network', 'nlp', 'computer vision']
            
            emerging_tech_count = sum(1 for tech in technologies 
                                     if any(e_tech in tech for e_tech in emerging_techs))
            
            tech_score = min(30, emerging_tech_count * 10)
            
            # Add points for novel combinations of technologies
            tech_combination_score = 0
            if 'blockchain' in ' '.join(technologies) and 'ai' in ' '.join(technologies):
                tech_combination_score += 10
            if 'quantum' in ' '.join(technologies):
                tech_combination_score += 15
            
            # Check topic novelty
            topic_novelty_score = 0
            if topics and "topics" in topics:
                for topic in topics["topics"]:
                    top_words = topic.get("top_words", [])
                    if 'novel' in top_words or 'innovation' in top_words or 'patent' in top_words:
                        topic_novelty_score += 5
                    if 'unique' in top_words or 'breakthrough' in top_words:
                        topic_novelty_score += 5
            
            topic_novelty_score = min(20, topic_novelty_score)
            
            # Calculate total innovation score
            innovation_score = base_score + tech_score + tech_combination_score + topic_novelty_score
            innovation_score = min(100, innovation_score)
            
            # Determine innovation level
            if innovation_score >= 80:
                innovation_level = "Highly Innovative"
            elif innovation_score >= 65:
                innovation_level = "Innovative"
            elif innovation_score >= 50:
                innovation_level = "Moderately Innovative"
            elif innovation_score >= 30:
                innovation_level = "Incrementally Innovative"
            else:
                innovation_level = "Conventional"
            
            # Identify innovative aspects
            innovative_aspects = []
            if emerging_tech_count > 0:
                innovative_aspects.append("Use of emerging technologies")
            if tech_combination_score > 0:
                innovative_aspects.append("Novel combination of technologies")
            if topic_novelty_score > 0:
                innovative_aspects.append("Novel approach or methodology")
            
            return {
                "score": innovation_score,
                "level": innovation_level,
                "innovative_aspects": innovative_aspects,
                "emerging_technologies_identified": emerging_tech_count,
                "technological_novelty": tech_score + tech_combination_score,
                "approach_novelty": topic_novelty_score
            }
            
        except Exception as e:
            logger.exception(f"Error calculating innovation score: {e}")
            return {
                "score": 50,
                "level": "Unknown",
                "error": str(e)
            }
    
    def _assess_market_potential(
        self, 
        topics: Dict[str, Any], 
        entities: Dict[str, List[str]],
        sentiment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess market potential based on whitepaper analysis.
        
        Args:
            topics: Topic analysis results
            entities: Extracted entities
            sentiment: Sentiment analysis results
            
        Returns:
            Dictionary with market potential assessment
        """
        try:
            # Extract technologies and companies
            technologies = entities.get("technologies", [])
            companies = entities.get("companies", [])
            
            # Calculate base market score
            base_score = 50
            
            # Adjust for technologies (some have more market potential)
            high_growth_techs = [
                'ai', 'blockchain', 'quantum', 'cloud', 'saas',
                'machine learning', 'data science', 'fintech'
            ]
            
            # Count occurrences of high-growth technologies
            high_growth_count = sum(1 for tech in technologies 
                                   if any(h_tech in tech for h_tech in high_growth_techs))
            
            tech_score = min(25, high_growth_count * 5)
            
            # Adjust for mentioned companies (more established companies = more market validation)
            company_score = min(15, len(companies) * 3)
            
            # Adjust for sentiment
            sentiment_score = sentiment.get("sentiment_score", 0) / 5  # -20 to +20 points
            
            # Calculate market size estimate
            market_size = "medium"
            if high_growth_count >= 3:
                market_size = "large"
            elif high_growth_count <= 1 and len(companies) <= 2:
                market_size = "small"
            
            # Calculate growth potential
            growth_potential = "medium"
            total_score = base_score + tech_score + company_score + sentiment_score
            if total_score >= 80:
                growth_potential = "high"
            elif total_score <= 40:
                growth_potential = "low"
            
            # Determine competition level
            competition_level = "medium"
            if len(companies) >= 5:
                competition_level = "high"
            elif len(companies) <= 1:
                competition_level = "low"
            
            return {
                "overall_score": min(100, int(total_score)),
                "market_size": market_size,
                "growth_potential": growth_potential,
                "competition_level": competition_level,
                "technology_relevance": tech_score,
                "market_validation": company_score,
                "sentiment_impact": sentiment_score
            }
            
        except Exception as e:
            logger.exception(f"Error assessing market potential: {e}")
            return {
                "overall_score": 50,
                "market_size": "medium",
                "growth_potential": "medium",
                "error": str(e)
            }
    
    def _generate_summary(self, results: Dict[str, Any]) -> str:
        """
        Generate a summary of whitepaper analysis.
        
        Args:
            results: Analysis results
            
        Returns:
            Summary text
        """
        try:
            # Extract key components for summary
            key_topics = []
            if "key_topics" in results and "topics" in results["key_topics"]:
                key_topics = [topic["name"] for topic in results["key_topics"]["topics"][:3]]
            
            technologies = []
            if "entities" in results and "technologies" in results["entities"]:
                technologies = results["entities"]["technologies"][:3]
            
            innovation = results.get("innovation_score", {})
            innovation_level = innovation.get("level", "Unknown")
            
            market = results.get("market_potential", {})
            growth_potential = market.get("growth_potential", "medium")
            market_size = market.get("market_size", "medium")
            
            sentiment = results.get("sentiment_analysis", {})
            overall_sentiment = sentiment.get("overall_sentiment", "neutral")
            
            # Generate summary text
            summary_parts = [
                f"This whitepaper focuses on {', '.join(key_topics) if key_topics else 'various topics'}.",
                f"It discusses technologies including {', '.join(technologies) if technologies else 'various technologies'}.",
                f"The document presents a {innovation_level.lower()} approach with {growth_potential} growth potential in a {market_size}-sized market.",
                f"Overall sentiment is {overall_sentiment}, with a {sentiment.get('sentiment_score', 0)} sentiment score."
            ]
            
            # Add complexity assessment
            complexity = results.get("complexity_metrics", {})
            if "reading_level" in complexity:
                summary_parts.append(
                    f"The paper is written at a {complexity['reading_level'].lower()} reading level "
                    f"(Flesch Reading Ease: {complexity.get('flesch_reading_ease', 0):.1f})."
                )
            
            return " ".join(summary_parts)
            
        except Exception as e:
            logger.exception(f"Error generating summary: {e}")
            return "Summary generation failed due to an error."
    
    def _check_cache(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """
        Check if analysis for this paper is already cached.
        
        Args:
            paper_id: Whitepaper ID
            
        Returns:
            Cached results or None
        """
        cache_file = self.cache_dir / f"{paper_id}_analysis.json"
        
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return None
    
    def _cache_results(self, paper_id: str, results: Dict[str, Any]) -> None:
        """
        Cache analysis results.
        
        Args:
            paper_id: Whitepaper ID
            results: Analysis results
        """
        try:
            cache_file = self.cache_dir / f"{paper_id}_analysis.json"
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to cache results for {paper_id}: {e}")
    
    def _find_common_topics(self, analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find common topics across multiple whitepapers.
        
        Args:
            analyses: List of whitepaper analyses
            
        Returns:
            List of common topics with paper IDs
        """
        # Extract all topics from all papers
        all_topics = {}
        
        for paper in analyses:
            paper_id = paper.get("paper_id", "unknown")
            topics = paper.get("key_topics", {}).get("topics", [])
            
            for topic in topics:
                topic_words = set(topic.get("top_words", []))
                topic_name = topic.get("name", "")
                
                # Check if this topic is similar to any existing topic
                matched = False
                for existing_topic, topic_data in all_topics.items():
                    existing_words = set(topic_data["words"])
                    # If there's significant word overlap, consider it the same topic
                    if len(topic_words.intersection(existing_words)) >= min(2, len(topic_words) // 2):
                        topic_data["papers"].append(paper_id)
                        topic_data["count"] += 1
                        matched = True
                        break
                
                # If no match, add as new topic
                if not matched:
                    all_topics[topic_name] = {
                        "name": topic_name,
                        "words": list(topic_words),
                        "papers": [paper_id],
                        "count": 1
                    }
        
        # Convert to list and sort by frequency
        common_topics = [topic_data for _, topic_data in all_topics.items()]
        common_topics.sort(key=lambda x: x["count"], reverse=True)
        
        return common_topics
    
    def _calculate_topic_similarity(self, analyses: List[Dict[str, Any]]) -> List[List[float]]:
        """
        Calculate similarity matrix between whitepapers based on topics.
        
        Args:
            analyses: List of whitepaper analyses
            
        Returns:
            2D similarity matrix
        """
        n = len(analyses)
        similarity_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        # Extract topic words for each paper
        paper_topics = []
        for paper in analyses:
            topic_words = set()
            topics = paper.get("key_topics", {}).get("topics", [])
            
            for topic in topics:
                topic_words.update(topic.get("top_words", []))
            
            paper_topics.append(topic_words)
        
        # Calculate Jaccard similarity between papers
        for i in range(n):
            for j in range(n):
                if i == j:
                    similarity_matrix[i][j] = 1.0  # Self-similarity is 1.0
                else:
                    # Jaccard similarity: |A ∩ B| / |A ∪ B|
                    intersection = len(paper_topics[i].intersection(paper_topics[j]))
                    union = len(paper_topics[i].union(paper_topics[j]))
                    similarity_matrix[i][j] = intersection / union if union > 0 else 0.0
        
        return similarity_matrix
    
    def _find_common_entities(self, analyses: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Find common entities across multiple whitepapers.
        
        Args:
            analyses: List of whitepaper analyses
            
        Returns:
            Dictionary with common entities
        """
        # Track entities across papers
        companies = {}
        technologies = {}
        
        for paper in analyses:
            paper_id = paper.get("paper_id", "unknown")
            entities = paper.get("entities", {})
            
            # Track companies
            for company in entities.get("companies", []):
                if company not in companies:
                    companies[company] = {"name": company, "papers": [], "count": 0}
                companies[company]["papers"].append(paper_id)
                companies[company]["count"] += 1
            
            # Track technologies
            for tech in entities.get("technologies", []):
                if tech not in technologies:
                    technologies[tech] = {"name": tech, "papers": [], "count": 0}
                technologies[tech]["papers"].append(paper_id)
                technologies[tech]["count"] += 1
        
        # Sort by frequency
        common_companies = sorted(
            companies.values(),
            key=lambda x: x["count"],
            reverse=True
        )
        
        common_technologies = sorted(
            technologies.values(),
            key=lambda x: x["count"],
            reverse=True
        )
        
        return {
            "companies": common_companies,
            "technologies": common_technologies
        }
    
    def _compare_sentiment(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare sentiment across multiple whitepapers.
        
        Args:
            analyses: List of whitepaper analyses
            
        Returns:
            Dictionary with sentiment comparison
        """
        sentiment_by_paper = {}
        
        for paper in analyses:
            paper_id = paper.get("paper_id", "unknown")
            sentiment = paper.get("sentiment_analysis", {})
            
            sentiment_by_paper[paper_id] = {
                "overall": sentiment.get("overall_sentiment", "neutral"),
                "score": sentiment.get("sentiment_score", 0)
            }
        
        # Calculate average sentiment score
        scores = [s.get("score", 0) for s in sentiment_by_paper.values()]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return {
            "by_paper": sentiment_by_paper,
            "average_score": avg_score,
            "most_positive": max(sentiment_by_paper.items(), key=lambda x: x[1]["score"])[0],
            "most_negative": min(sentiment_by_paper.items(), key=lambda x: x[1]["score"])[0]
        }
    
    def _generate_comparative_summary(
        self,
        analyses: List[Dict[str, Any]],
        common_topics: List[Dict[str, Any]],
        topic_similarity: List[List[float]],
        innovation_comparison: Dict[str, int],
        market_potential_comparison: Dict[str, int]
    ) -> str:
        """
        Generate summary comparing multiple whitepapers.
        
        Args:
            analyses: List of whitepaper analyses
            common_topics: Common topics across papers
            topic_similarity: Topic similarity matrix
            innovation_comparison: Innovation scores by paper
            market_potential_comparison: Market potential scores by paper
            
        Returns:
            Comparative summary text
        """
        try:
            n_papers = len(analyses)
            paper_ids = [paper.get("paper_id", f"paper_{i}") for i, paper in enumerate(analyses)]
            
            # Identify most common topics
            top_topics = [topic["name"] for topic in common_topics[:3]] if common_topics else []
            
            # Identify papers with highest similarity
            highest_similarity = 0.0
            most_similar_pair = (0, 0)
            
            for i in range(n_papers):
                for j in range(i+1, n_papers):
                    if topic_similarity[i][j] > highest_similarity:
                        highest_similarity = topic_similarity[i][j]
                        most_similar_pair = (i, j)
            
            # Find most innovative paper
            most_innovative = max(innovation_comparison.items(), key=lambda x: x[1])[0]
            
            # Find highest market potential
            highest_market_potential = max(market_potential_comparison.items(), key=lambda x: x[1])[0]
            
            # Generate summary
            summary_parts = [
                f"Comparative analysis of {n_papers} whitepapers shows the following insights:",
                f"Common themes across papers include: {', '.join(top_topics) if top_topics else 'No strong common themes'}.",
                f"Papers {paper_ids[most_similar_pair[0]]} and {paper_ids[most_similar_pair[1]]} show the highest topical similarity.",
                f"The most innovative approach is presented in {most_innovative}.",
                f"The highest market potential is shown by {highest_market_potential}."
            ]
            
            return " ".join(summary_parts)
            
        except Exception as e:
            logger.exception(f"Error generating comparative summary: {e}")
            return "Comparative summary generation failed due to an error."
    
    def _identify_sectors(
        self, key_topics: Dict[str, Any], technologies: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Identify potential investment sectors based on whitepaper topics.
        
        Args:
            key_topics: Topic analysis results
            technologies: Extracted technologies
            
        Returns:
            List of identified sectors with confidence
        """
        # Define sector mapping for common technologies and topics
        sector_keywords = {
            "Financial Services": ["banking", "fintech", "payment", "lending", "insurance", "invest"],
            "Information Technology": ["software", "cloud", "saas", "platform", "api"],
            "Healthcare": ["health", "medical", "patient", "clinical", "biotech"],
            "Cybersecurity": ["security", "cyber", "encryption", "privacy", "threat"],
            "Artificial Intelligence": ["ai", "machine learning", "deep learning", "neural", "nlp"],
            "Blockchain": ["blockchain", "crypto", "token", "defi", "bitcoin", "ethereum"],
            "E-commerce": ["retail", "commerce", "marketplace", "shop", "consumer"],
            "Energy": ["energy", "renewable", "solar", "carbon", "climate"]
        }
        
        # Count matches for each sector
        sector_scores = {}
        
        # Extract topic words
        topic_words = []
        if "topics" in key_topics:
            for topic in key_topics["topics"]:
                topic_words.extend(topic.get("top_words", []))
        
        # Combine with technologies
        all_terms = ' '.join(topic_words + technologies).lower()
        
        # Score each sector
        for sector, keywords in sector_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in all_terms:
                    score += 1
            
            if score > 0:
                confidence = "low"
                if score >= 3:
                    confidence = "high"
                elif score >= 2:
                    confidence = "medium"
                
                sector_scores[sector] = {
                    "sector": sector,
                    "confidence": confidence,
                    "score": score
                }
        
        # Sort by score and return
        sectors = list(sector_scores.values())
        sectors.sort(key=lambda x: x["score"], reverse=True)
        
        return sectors
    
    def _filter_public_companies(self, companies: List[str]) -> List[str]:
        """
        Filter list to identify likely public companies.
        
        Args:
            companies: List of company names
            
        Returns:
            List of likely public companies
        """
        # In a real implementation, this would check against a database of public companies
        # For this example, use a simple list of well-known public companies
        public_companies = {
            'apple', 'google', 'microsoft', 'amazon', 'facebook', 'meta',
            'tesla', 'nvidia', 'amd', 'intel', 'ibm', 'oracle', 'salesforce',
            'jpmorgan', 'goldman sachs', 'morgan stanley', 'bank of america'
        }
        
        return [company for company in companies if company.lower() in public_companies]
    
    def _assess_technology_maturity(
        self, technologies: List[str], key_topics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess the maturity level of technologies mentioned in whitepaper.
        
        Args:
            technologies: List of technologies
            key_topics: Topic analysis results
            
        Returns:
            Dictionary with technology maturity assessment
        """
        # Define maturity levels for common technologies
        technology_maturity = {
            "blockchain": "emerging",
            "cryptocurrency": "emerging",
            "quantum computing": "nascent",
            "artificial intelligence": "growing",
            "machine learning": "growing",
            "deep learning": "growing",
            "cloud computing": "mature",
            "saas": "mature",
            "big data": "mature",
            "internet of things": "growing",
            "5g": "growing",
            "virtual reality": "emerging",
            "augmented reality": "emerging"
        }
        
        # Assess each technology
        assessments = []
        for tech in technologies:
            maturity = "unknown"
            for known_tech, level in technology_maturity.items():
                if known_tech in tech.lower():
                    maturity = level
                    break
            
            assessments.append({
                "technology": tech,
                "maturity": maturity
            })
        
        # Determine overall maturity
        maturity_counts = {"nascent": 0, "emerging": 0, "growing": 0, "mature": 0, "unknown": 0}
        for assessment in assessments:
            maturity_counts[assessment["maturity"]] += 1
        
        # Calculate weighted score (higher = more mature)
        maturity_weights = {"nascent": 1, "emerging": 2, "growing": 3, "mature": 4, "unknown": 2.5}
        total_weight = sum(maturity_counts[level] * maturity_weights[level] for level in maturity_counts)
        count = sum(maturity_counts.values()) or 1  # Avoid division by zero
        
        maturity_score = total_weight / count
        
        # Determine overall maturity level
        if maturity_score < 1.75:
            overall_maturity = "nascent"
        elif maturity_score < 2.5:
            overall_maturity = "emerging"
        elif maturity_score < 3.25:
            overall_maturity = "growing"
        else:
            overall_maturity = "mature"
        
        return {
            "overall_maturity": overall_maturity,
            "maturity_score": round(maturity_score, 2),
            "technology_assessments": assessments
        }
    
    def _generate_investment_thesis(
        self,
        key_topics: Dict[str, Any],
        sectors: List[Dict[str, Any]],
        companies: List[str],
        technologies: List[str],
        sentiment: str,
        growth_potential: str
    ) -> str:
        """
        Generate an investment thesis based on whitepaper analysis.
        
        Args:
            key_topics: Topic analysis results
            sectors: Identified sectors
            companies: Identified companies
            technologies: Identified technologies
            sentiment: Overall sentiment
            growth_potential: Market growth potential
            
        Returns:
            Investment thesis text
        """
        # Extract main sector
        main_sector = sectors[0]["sector"] if sectors else "technology"
        
        # Extract key technologies
        key_techs = technologies[:3] if technologies else ["technology"]
        
        # Extract relevant companies
        relevant_companies = companies[:3] if companies else []
        
        # Generate thesis based on sentiment and growth potential
        if sentiment == "positive" and growth_potential == "high":
            thesis = (
                f"The whitepaper presents a compelling investment opportunity in the {main_sector} sector, "
                f"specifically in {', '.join(key_techs)}. "
                f"The high growth potential and positive industry outlook suggest strong returns on investment. "
            )
        elif sentiment == "positive":
            thesis = (
                f"The {main_sector} sector shows promising investment potential, particularly in "
                f"{', '.join(key_techs)}. While growth may be moderate, the positive industry sentiment "
                f"indicates stability and sustainable returns. "
            )
        elif growth_potential == "high":
            thesis = (
                f"Despite mixed sentiment, the {main_sector} sector and particularly {', '.join(key_techs)} "
                f"show high growth potential. Early-stage investment could yield strong returns as the "
                f"market matures and technology adoption increases. "
            )
        else:
            thesis = (
                f"The {main_sector} sector, including {', '.join(key_techs)}, presents a moderate "
                f"investment opportunity. A cautious approach is warranted given the mixed sentiment "
                f"and growth projections. "
            )
        
        # Add company information if available
        if relevant_companies:
            thesis += (
                f"Key players in this space include {', '.join(relevant_companies)}, which may "
                f"represent direct investment opportunities or strategic partnerships. "
            )
        
        return thesis
    
    def _identify_risks(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify investment risks based on whitepaper analysis.
        
        Args:
            analysis: Whitepaper analysis results
            
        Returns:
            List of identified risks
        """
        risks = []
        
        # Check technology maturity
        tech_maturity = analysis.get("tech_maturity", {}).get("overall_maturity", "unknown")
        if tech_maturity in ["nascent", "emerging"]:
            risks.append({
                "category": "Technology Risk",
                "description": f"Technology is in {tech_maturity} stage and may not achieve market adoption.",
                "severity": "high" if tech_maturity == "nascent" else "medium"
            })
        
        # Check market potential
        market = analysis.get("market_potential", {})
        market_size = market.get("market_size", "medium")
        competition = market.get("competition_level", "medium")
        
        if market_size == "small":
            risks.append({
                "category": "Market Risk",
                "description": "Limited market size may constrain growth potential.",
                "severity": "medium"
            })
        
        if competition == "high":
            risks.append({
                "category": "Competitive Risk",
                "description": "Highly competitive market may pressure margins and market share.",
                "severity": "high"
            })
        
        # Check sentiment
        sentiment = analysis.get("sentiment_analysis", {})
        if sentiment.get("overall_sentiment") == "negative":
            risks.append({
                "category": "Industry Sentiment Risk",
                "description": "Negative industry sentiment may impact investment returns.",
                "severity": "medium"
            })
        
        # Check innovation score
        innovation = analysis.get("innovation_score", {})
        if innovation.get("score", 50) < 40:
            risks.append({
                "category": "Innovation Risk",
                "description": "Low innovation level may lead to obsolescence or disruption.",
                "severity": "medium"
            })
        
        # Check regulatory mentions
        entities = analysis.get("entities", {})
        if entities.get("regulatory_bodies", []):
            risks.append({
                "category": "Regulatory Risk",
                "description": "Regulatory considerations may impact market development.",
                "severity": "high"
            })
        
        # If no specific risks identified, add a generic risk
        if not risks:
            risks.append({
                "category": "General Investment Risk",
                "description": "All investments carry inherent risks of capital loss.",
                "severity": "medium"
            })
        
        return risks
    
    def _calculate_confidence(self, analysis: Dict[str, Any]) -> int:
        """
        Calculate confidence level in the investment insights.
        
        Args:
            analysis: Whitepaper analysis results
            
        Returns:
            Confidence score (0-100)
        """
        # Base confidence
        confidence = 50
        
        # Adjust based on data quality
        text_length = analysis.get("text_length", 0)
        if text_length > 10000:
            confidence += 10
        elif text_length < 2000:
            confidence -= 10
        
        # Adjust based on entities identified
        entities = analysis.get("entities", {})
        company_count = len(entities.get("companies", []))
        tech_count = len(entities.get("technologies", []))
        
        if company_count > 5:
            confidence += 5
        if tech_count > 5:
            confidence += 5
        
        # Adjust based on sentiment confidence
        sentiment = analysis.get("sentiment_analysis", {})
        sentiment_distr = sentiment.get("distribution", {})
        
        # If sentiment is heavily skewed in one direction, increase confidence
        max_sentiment = max(sentiment_distr.values()) if sentiment_distr else 0
        if max_sentiment > 70:
            confidence += 5
        
        # Adjust based on complexity metrics
        complexity = analysis.get("complexity_metrics", {})
        if complexity.get("lexical_diversity", 0) > 0.4:
            confidence += 5
        
        # Ensure confidence is in range 0-100
        confidence = max(0, min(100, confidence))
        
        return confidence
    
    # Methods for generating simulated whitepaper text
    def _generate_blockchain_whitepaper_text(self) -> str:
        """Generate simulated blockchain whitepaper text."""
        return """
        # Blockchain Technology: Transforming Financial Markets
        
        ## Abstract
        
        This whitepaper explores the transformative potential of blockchain technology in financial markets. We present a novel approach to decentralized finance (DeFi) that addresses existing limitations in liquidity, scalability, and security. Our proposed solution leverages a hybrid consensus mechanism and layer-2 scaling to enable high-throughput transaction processing while maintaining decentralization.
        
        ## Introduction
        
        Blockchain technology has emerged as a disruptive force in financial services, enabling peer-to-peer transactions without intermediaries. Despite significant progress, challenges remain in areas of scalability, interoperability, and regulatory compliance. This paper introduces a new blockchain architecture designed specifically for financial applications.
        
        ## Technology Overview
        
        Our solution combines the security of Proof-of-Stake with the efficiency of a Directed Acyclic Graph (DAG) structure. This hybrid approach enables:
        
        - Transaction throughput of 10,000+ TPS
        - Sub-second finality
        - Cross-chain interoperability
        - Regulatory compliance mechanisms
        
        The system incorporates smart contracts compatible with Ethereum's EVM while extending functionality through native financial primitives. These include automated market makers, lending protocols, and synthetic asset creation.
