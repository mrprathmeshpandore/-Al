import { useState, useEffect } from 'react';

/**
 * Animated Count Up Hook triggered on view
 * @param {number} targetTarget - Target number
 * @param {boolean} isInView - Framer motion inView status
 * @param {number} durationMs - Duration in milliseconds
 */
export function useCountUp(targetNumber, isInView, durationMs = 1800) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!isInView) return;

    let startTimestamp = null;
    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / durationMs, 1);
      // Ease out cubic function
      const easeProgress = 1 - Math.pow(1 - progress, 3);
      setCount(Math.floor(easeProgress * targetNumber));

      if (progress < 1) {
        window.requestAnimationFrame(step);
      }
    };

    const animationFrame = window.requestAnimationFrame(step);
    return () => window.cancelAnimationFrame(animationFrame);
  }, [targetNumber, isInView, durationMs]);

  return count;
}
