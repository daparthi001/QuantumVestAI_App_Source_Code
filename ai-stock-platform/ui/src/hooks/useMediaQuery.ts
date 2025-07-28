import { useEffect, useState } from 'react';

/**
 * useMediaQuery hook
 * Returns true if the media query matches.
 */
const useMediaQuery = (query: string): boolean => {
  const getMatches = () =>
    typeof window !== 'undefined' ? window.matchMedia(query).matches : false;

  const [matches, setMatches] = useState<boolean>(getMatches());

  useEffect(() => {
    const media = window.matchMedia(query);
    const listener = () => setMatches(media.matches);

    // Support older Safari
    if (media.addEventListener) {
      media.addEventListener('change', listener);
    } else {
      media.addListener(listener);
    }

    setMatches(media.matches);

    return () => {
      if (media.removeEventListener) {
        media.removeEventListener('change', listener);
      } else {
        media.removeListener(listener);
      }
    };
  }, [query]);

  return matches;
};

export default useMediaQuery;
