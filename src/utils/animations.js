// Framer Motion Animation System & Reusable Variants

export const fadeIn = {
  hidden: { opacity: 0 },
  visible: { 
    opacity: 1, 
    transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] } 
  }
};

export const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { 
    opacity: 1, 
    y: 0, 
    transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] } 
  }
};

export const scaleIn = {
  hidden: { opacity: 0, scale: 0.85, y: 20 },
  visible: { 
    opacity: 1, 
    scale: 1, 
    y: 0, 
    transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] } 
  }
};

export const slideLeft = {
  hidden: { opacity: 0, x: -60 },
  visible: { 
    opacity: 1, 
    x: 0, 
    transition: { duration: 0.7, ease: [0.16, 1, 0.3, 1] } 
  }
};

export const slideRight = {
  hidden: { opacity: 0, x: 60 },
  visible: { 
    opacity: 1, 
    x: 0, 
    transition: { duration: 0.7, ease: [0.16, 1, 0.3, 1] } 
  }
};

export const staggerContainer = (staggerTime = 0.12, delayTime = 0.1) => ({
  hidden: {},
  visible: {
    transition: {
      staggerChildren: staggerTime,
      delayChildren: delayTime
    }
  }
});

export const heroBadgeVariant = {
  hidden: { opacity: 0, y: 15, scale: 0.95 },
  visible: { 
    opacity: 1, 
    y: 0, 
    scale: 1, 
    transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] } 
  }
};

export const buttonTapHover = {
  rest: { scale: 1 },
  hover: { 
    scale: 1.03, 
    transition: { duration: 0.2, ease: "easeOut" } 
  },
  tap: { 
    scale: 0.97, 
    transition: { duration: 0.1, ease: "easeIn" } 
  }
};

export const iconInteractiveHover = {
  rest: { scale: 1, rotate: 0 },
  hover: { 
    scale: 1.05, 
    rotate: 3, 
    transition: { duration: 0.25, ease: "easeOut" } 
  }
};

export const avatarStaggerVariant = {
  hidden: { opacity: 0, scale: 0.7 },
  visible: { 
    opacity: 1, 
    scale: 1, 
    transition: { duration: 0.35, ease: "backOut" } 
  }
};
