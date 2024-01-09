# TodoMVC using HTMX + HYPERSCRIPT + PYTHON FLASK • 

> htmx gives you access to AJAX, CSS Transitions, WebSockets and Server Sent Events directly in HTML, using attributes, so you can build modern user interfaces with the simplicity and power of hypertext

> hyperscript - An easy & approachable language for modern web front-ends. Enhance HTML with concise DOM, event and async features. Make writing interactive HTML a joy.


## Resources

- [HTMX Website](https://htmx.org)
- [HTMX Documentation](https://htmx.org/docs/)
- [Hyperscript Documentation](https://hyperscript.org/docs/)

### How to Run Demo

1. checkout repo
2. Install todomvc dependencies 
```npm install```
3. Ensure you have [flask installed](https://flask.palletsprojects.com/en/3.0.x/installation/)
4. ```flask run```
5. Access app on http://127.0.0.1:5000
## Implementation

This implementation of TodoMVC is a prototype to evaluate HTMX along with minimal hyperscript. Since TodoMVC was designed to evaluate full frontend-only frameworks (usually JS, TS), this is an attempt to see how far we can get SPA features with using plain HTML enhanced with HTMX and where if at all we need some scripting how elegant (or not) Hyperscript can be used.

Some key violations from the [TodoMVC spec](https://github.com/tastejs/todomvc/blob/master/app-spec.md) which was not considered important for this prototype are

* Does not use localStorage. Session is held in cookies and state processed on server side.
* You need a server to run the demo.

### Notes on Flask Server implementation

The server side has been kept minimal and simple. Spartan. It is not likely idiomatic.


## Credit

Created by [Pradeep Roark](http://pradeeproark.com)
