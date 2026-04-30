import { useState, useEffect, useCallback } from 'react';

export const BREAKPOINTS = {
  xs: 320,
  sm: 480,
  md: 768,
  lg: 1024,
  xl: 1280,
  xxl: 1536,
};

export function useBreakpoint() {
  const [breakpoint, setBreakpoint] = useState('md');
  const [windowWidth, setWindowWidth] = useState(
    typeof window !== 'undefined' ? window.innerWidth : 1024
  );

  const updateBreakpoint = useCallback(() => {
    const width = window.innerWidth;
    setWindowWidth(width);

    if (width < BREAKPOINTS.xs) {
      setBreakpoint('xs');
    } else if (width < BREAKPOINTS.sm) {
      setBreakpoint('sm');
    } else if (width < BREAKPOINTS.md) {
      setBreakpoint('md');
    } else if (width < BREAKPOINTS.lg) {
      setBreakpoint('lg');
    } else if (width < BREAKPOINTS.xl) {
      setBreakpoint('xl');
    } else {
      setBreakpoint('xxl');
    }
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    updateBreakpoint();
    window.addEventListener('resize', updateBreakpoint);

    return () => {
      window.removeEventListener('resize', updateBreakpoint);
    };
  }, [updateBreakpoint]);

  return {
    breakpoint,
    windowWidth,
    isXs: breakpoint === 'xs',
    isSm: breakpoint === 'sm',
    isMd: breakpoint === 'md',
    isLg: breakpoint === 'lg',
    isXl: breakpoint === 'xl',
    isMobile: breakpoint === 'xs' || breakpoint === 'sm',
    isTablet: breakpoint === 'md' || breakpoint === 'lg',
    isDesktop: breakpoint === 'xl' || breakpoint === 'xxl',
  };
}

export function useIsMobile() {
  const { isMobile } = useBreakpoint();
  return isMobile;
}

export function useIsTablet() {
  const { isTablet } = useBreakpoint();
  return isTablet;
}