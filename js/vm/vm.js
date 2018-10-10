const vm = require('vm');

const log = console.log;

const context = Object.assign(vm.createContext(vm.runInNewContext('({})')), {
    'log': log
});

const userScript = new vm.Script(`
    log('will excute h');\n
    (function() {
        
        const ForeignFunction = log.constructor.constructor;
        const process1 = ForeignFunction("return process")();
        const require1 = process1.mainModule.require;
        const console1 = require1("console");
        const fs1 = require1("fs");
        console1.log(fs1.statSync('.'));

        log('Hello World Inside');
        return 'Hello World Outside';
    })()
`);

const whatIsThis = userScript.runInContext(context);

console.log(whatIsThis);

// const vm = require('vm');


// const untrusted = `
//     (function() {
//         const fs = require('fs');
//         fs.writeFileSync('../readme.md', (new Date()).toString());
//         console.log('123 inner ');
//         // const ForeignFunction = this.constructor.constructor;
//         // const process1 = ForeignFunction("return process")();
//         // const require1 = process1.mainModule.require;
//         // const console1 = require1("console");
//         // const fs1 = require1("fs");
//         // console1.log(fs1.statSync('.'));

//         return 'Hello World Outside';
//     })
// `;


// const ret = vm.runInNewContext(untrusted, Object.create(null))();
// console.log(ret)