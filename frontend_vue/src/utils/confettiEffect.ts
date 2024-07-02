//@ts-ignore
import confetti from 'canvas-confetti';

export function launchConfetti() {
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
    origin: { y: 0.9 },
    colors: ['#F2059F', '#04D9B2', '#80C7F2'],
  });

  setTimeout(() => {
    confettiCanvas.remove();
  }, 2000);
}
