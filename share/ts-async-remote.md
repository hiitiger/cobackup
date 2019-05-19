
# electron中，使用TS3.0/2.8生成TypeScript版的异步remote接口

在electron使用中经常遇到的情况是需要在renderer进程和browser进程间通信，electron本身提供了remote和ipc模块，其中remote提供了rpc风格的调用。

```JS
const {BrowserWindow} = require('electron').remote
let win = new BrowserWindow({width: 800, height: 600})
win.loadURL('https://github.com')
```
**问题**:remote是同步调用的，在一些场景下，可能并不合适，我们需要完全异步的调用。

这时可以自己封装ipc通信成为较高级的rpc风格的api调用，electron-remote 提供了此类功能。

**问题**:当我们需要调用自己的接口，且使用TypeScript时，我们期望可以将远程的interface生成一个异步的promise化的代理接口类型，在TS开发中带有**类型提示**，这时可能的选择是通过工具来生成新的Promisefied接口，然后自己封装ipc调用。

```JS
//interface define
interface IEchoService {
  echo(content: string): string;
  echo2(content: string): Promise<string>;
  echoMul(a: string, n: number): string;
}

//what we want 
interface IEchoServiceAsync { //Promisefied<IEchoService>
  echo(content: string): Promise<string>;
  echo2(content: string): Promise<string>;
  echoMul(a: string, n: number): Promise<string>;
}

//so in general 
//we have interface IXXService
//we want Promisefied<IXXService>
```

利用TypeScript3.0和2.8的新特性，可以很方便的创建一个新的Promise化的类型。

首先我们期望可以创建一个代理对象，当然，promise化的类型必须是generic的，所以期望代码是这样的
```JS
type PromisifiedFunction<T> = ...

type Promisified<T> = {
  [K in keyof T]:  PromisifiedFunction<T[K]>
};

function createService<T>(name: string): Promisified<T> {...}

const echoService = createService<IEchoService>("EchoService", ...);
echoService.echo("hello").then((res) => {console.log(res)})
```

这里关键是生存promise化的function，利用TS2.8的条件类型
```JS
type PromisifiedFunction<T extends (...args: any[]) => any> = T extends (...args: any[]) => infer U ? (...args: any[]) => Promise<U> : T

function bfunc(a: string, b: number) {
  return a.repeat(b)
}

let afunc : PromisifiedFunction<typeof bfunc>  //(...args: any[]) => Promise<string>
```

完整的代码，同时判断一下函数返回类型是否已经是promise
```JS
type AnyFunction = (...args: any[]) => any;

type Unpacked<T> = T extends Promise<infer U> ? U : T;

type PromisifiedFunction<T extends (...args: any[]) => any> = T extends (...args: any[]) => infer U ? (...args: any[]) => Promise<Unpacked<U>> : T

type Promisified<T> = {
    [K in keyof T]: T[K] extends AnyFunction ? PromisifiedFunction<T[K]> : never
}

function createService<T>(name: string): Promisified<T> {
  const proxy = new Proxy(...)
  return proxy as Promisified<T>;
}
```

```js
//use it
const echoService = createService<IEchoService>("EchoService");
echoService.echo("command").then((res) => {
  console.log(res);
}
```

当然，这里有个小问题，VSCode里可以看到echoService.echo 的类型提示是 
```JS
(method) echo(...args: any[]): Promise<string>

```


好在TS3.0有了Rest parameters，修改一下
```JS
type AnyFunction<U extends any[], V> = (...args: U) => V;

type Unpacked<T> = T extends Promise<infer U> ? U : T;

type PromisifiedFunction<T> = T extends AnyFunction<infer U, infer V>
  ? (...args: U) => Promise<Unpacked<V>>
  : never;

type Promisified<T> = {
  [K in keyof T]: T[K] extends AnyFunction<infer U, infer V>
    ? PromisifiedFunction<T[K]>
    : never
};
```

此时VSCode里可以看到echoService.echo 的类型提示是 
```JS
(method) echo(content: string): Promise<string>
```

完整的示例可以参考 

https://github.com/hiitiger/electron-demos/tree/master/ipc-async-interface-proxy