// This is just a copy of
// https://github.com/simplesmiler/vue-clickaway/

// Tried to make it compatible with Vue 3
// Updates required on directives:
// https://v3-migration.vuejs.org/breaking-changes/custom-directives.html

const HANDLER = '_vue_clickaway_handler';

function unbind(el: ClickAwayElement): void {
  if (el[HANDLER]) {
    document.documentElement.removeEventListener('click', el[HANDLER], false);
    delete el[HANDLER];
  }
}

interface ClickAwayBinding {
  value: (event: MouseEvent) => void;
  oldValue?: (event: MouseEvent) => void;
  name: string;
  rawName: string;
}

interface ClickAwayVNode {
  appContext: any;
}

interface ClickAwayElement extends HTMLElement {
  [HANDLER]?: (event: MouseEvent) => void | null;
}

function bind(el: ClickAwayElement, binding: ClickAwayBinding, vnode: ClickAwayVNode): void {
  unbind(el);

  const vm = vnode.appContext;

  const callback = binding.value;
  if (typeof callback !== 'function') {
    if (import.meta.env.MODE !== 'production') {
      console.warn(
        `v-${binding.name}="${
          binding.rawName}" expects a function value, `
        + `got ${callback}`,
      );
    }
    return;
  }

  // @NOTE: Vue binds directives in microtasks, while UI events are dispatched
  //        in macrotasks. This causes the listener to be set up before
  //        the "origin" click event (the event that lead to the binding of
  //        the directive) arrives at the document root. To work around that,
  //        we ignore events until the end of the "initial" macrotask.
  // @REFERENCE: https://jakearchibald.com/2015/tasks-microtasks-queues-and-schedules/
  // @REFERENCE: https://github.com/simplesmiler/vue-clickaway/issues/8

  let initialMacrotaskEnded: boolean = false;
  setTimeout(() => {
    initialMacrotaskEnded = true;
  }, 0);

  el[HANDLER] = function (ev: MouseEvent): void | null {
    const path: EventTarget[] | undefined = (ev as any).path || (ev.composedPath ? ev.composedPath() : undefined);
    if (initialMacrotaskEnded && (path ? !path.includes(el) : !el.contains(ev.target as Node))) {
      return callback.call(vm, ev);
    }
    return null;
  };

  document.documentElement.addEventListener('click', el[HANDLER], true);
}

const onClickaway = {
  mounted(el: ClickAwayElement, binding: ClickAwayBinding, vnode: ClickAwayVNode) {
    bind(el, binding, vnode);
  },
  updated(el: ClickAwayElement, binding: ClickAwayBinding, vnode: ClickAwayVNode) {
    if (binding.value === binding.oldValue) return;
    bind(el, binding, vnode);
  },
  unmounted(el: ClickAwayElement) {
    unbind(el);
  },
};

export { onClickaway };
