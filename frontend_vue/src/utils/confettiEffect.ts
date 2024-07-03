//@ts-ignore
import confetti from 'canvas-confetti';
import { TOKEN_COLOR_PALETTES } from '@/components/constants';

export function launchConfetti(token_type: string) {
  const confettiCanvas = document.createElement('canvas');
  const modal = document.querySelector('.vfm__content');
  modal?.appendChild(confettiCanvas);

  Object.assign(confettiCanvas.style, {
    position: 'absolute',
    top: '0',
    left: '0',
    width: '100%',
    height: '100%',
    pointerEvents: 'none',
  });

  Object.assign(confettiCanvas, {
    with: window.innerWidth,
    height: window.innerHeight,
  });

  const myConfetti = confetti.create(confettiCanvas, { resize: true });

  myConfetti({
    particleCount: 100,
    spread: 160,
    origin: { y: .4 },
    colors: TOKEN_COLOR_PALETTES[token_type],
  });

  setTimeout(() => {
    confettiCanvas.remove();
  }, 2000);
}
