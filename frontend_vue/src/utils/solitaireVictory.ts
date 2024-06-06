type oldPosType = {
  left: number;
  top: number;
};

export default function solitaireVictory(target: HTMLElement[], index: number) {
  const randomStagger = Math.floor(Math.random() * (200 - 100 + 1)) + 100;
  const randomSteps = Math.floor(Math.random() * (20 - 10 + 1)) + 10;
  const randomDirection = Math.random() < 0.5 ? true : false;
  const randomDelay = 500 * index;

  const g = -3; // Gravity
  const dt = randomSteps; // Time step
  const bounce = 0.7; // Bounce factor
  const endVelocity = 20; // End velocity
  const stagger = randomStagger; // Stagger time
  const clear = false; // Whether to clear existing clones
  const fallToLeft = randomDirection; // Whether to fall to the left
  const delay = randomDelay; // Animation delay

  const body = document.body;
  const windowHeight = window.innerHeight;

  const fallIteration = function (
    elem: HTMLElement,
    elemHeight: number,
    oldPos: oldPosType,
    dx: number,
    dy: number
  ) {
    const copy = elem.cloneNode(true) as HTMLElement;
    body.appendChild(copy);

    const newTop = Math.min(windowHeight - elemHeight, oldPos.top + dy);
    const newPos = {
      left: oldPos.left + dx,
      top: newTop,
    };
    copy.style.left = newPos.left + 'px';
    copy.style.top = newPos.top + 'px';
    if (Math.abs(newTop - (windowHeight - elemHeight)) < 5) {
      if (dy < 0 || dy > endVelocity) {
        dy *= -1 * bounce;
        setTimeout(function () {
          fallIteration(copy, elemHeight, newPos, dx, dy);
        }, dt);
      }
    } else {
      dy = dy - g;
      setTimeout(function () {
        fallIteration(copy, elemHeight, newPos, dx, dy);
      }, dt);
    }
  };

  const startFall = function (
    elem: HTMLElement,
    height: number,
    width: number,
    stagger: number
  ) {
    let dx = Math.floor(Math.random() * 10) + 5;
    if (fallToLeft) {
      dx = -dx;
    }
    const copy = elem.cloneNode(true) as HTMLElement;
    copy.classList.add('solitaire-victory-clone');
    copy.style.width = width + 'px';
    copy.style.height = height + 'px';
    copy.style.position = 'fixed';
    copy.style.zIndex = '1000';
    const originalOffset = elem.getBoundingClientRect();
    copy.style.left = originalOffset.left + 'px';
    copy.style.top = originalOffset.top + 'px';
    body.appendChild(copy);
    setTimeout(function () {
      fallIteration(
        copy,
        height,
        {
          left: originalOffset.left,
          top: originalOffset.top,
        },
        dx,
        0
      );
    }, stagger);
  };

  if (clear) {
    const clones = document.querySelectorAll('.solitaire-victory-clone');
    clones.forEach(function (clone) {
      clone.parentNode?.removeChild(clone);
    });
  }

  target.forEach(function (elem, index) {
    const rect = elem.getBoundingClientRect();
    if (rect.top >= 0 && rect.bottom <= window.innerHeight) {
      if (!elem.classList.contains('solitaire-victory-clone')) {
        setTimeout(() => {
          startFall(elem, elem.offsetHeight, elem.offsetWidth, index * stagger);
        }, delay);
      }
    }
  });
}
