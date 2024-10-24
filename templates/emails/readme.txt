This is an MJML file. MJML (Mailjet Markup Language) is a markup language designed to reduce the pain of coding responsive email templates.
It abstracts away the complexity of responsive email design, allowing developers to write simpler and more readable code.

There are many ways you can use MJML. The easier one that requires less setup is:
1. Add a mjml plugin to your code editor. This will allow you to write MJML code and see the rendered email template in real-time.
For VScode https://marketplace.visualstudio.com/items?itemName=attilabuti.vscode-mjml
( If you face troubles with the official plugin, try one of the forked projects )
2. Use the MJML online editor to convert mjml code to html: https://mjml.io/try-it-live

Or install MJML globally and compile your MJML files into HTML files:
1. Install MJML: `npm install -g mjml`.
2. Create an MJML file: Write your email template using MJML tags.
3. Compile the MJML file: Use the command `mjml input.mjml -o output.html` to compile your MJML file into an HTML file.
4. Use the generated HTML: The output HTML file can be used in your email campaigns.


For more information, and more visit the official MJML documentation: https://mjml.io/documentation

NOTE: When exporting to html, the conditions {% if BasicDetails['something'] %} living outside a <mj-text> are not supported and will be removed from the final html file.
If you need to use conditions, remeber to check the output html file and add them manually if needed.
