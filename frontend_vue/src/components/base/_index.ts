// Globally register all base components for convenience, because they
// will be used very frequently. Components are registered using the
// PascalCased version of their file name.

function registertBaseComponents(app: any) {
    const componentFiles = import.meta.glob(
        './_Base*.vue', { eager: true }
    );


    Object.entries(componentFiles).forEach(([path, m]) => {
        // Get the component config
        const componentConfig: any = m;
        // Get the PascalCase version of the component name
        const componentName = path
            // Remove the "./_" from the beginning
            .replace(/^\.\/_/, '')
            // Remove the file extension from the end
            .replace(/\.\w+$/, '');

        // Globally register the component
        app.component(componentName, componentConfig.default || componentConfig);
    });
}

export default registertBaseComponents;
