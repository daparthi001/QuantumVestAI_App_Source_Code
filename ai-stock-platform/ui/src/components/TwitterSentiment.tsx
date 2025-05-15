// Update the error handling in the component

useEffect(() => {
  const fetchSentiment = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`/api/social/twitter/sentiment/${ticker}`);
      setSentiment(response.data);
    } catch (err: any) {
      // Check if this is a configuration error (HTTP 503)
      if (err.response && err.response.status === 503) {
        setError('Twitter integration not configured. Please set up Twitter API credentials.');
      } else {
        setError('Failed to load Twitter sentiment data');
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Rest of the effect...
}, [ticker]);