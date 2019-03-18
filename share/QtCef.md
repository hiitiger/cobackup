# Why Qt - MOC反射小用


用过Qt的童鞋都了解Qt利用MOC实现了一些有趣的功能，比如反射、signal slot等。而Qt所带的这些特色功能时常能帮我们解决一些有趣的问题。

最近工作的一个活让我有点怀念Qt了。几年前在某个Qt项目里，需要接入Cef，作为一个Qt中的Web控件来使用，这是个很常见的功能，也有一票的现成代码可以copy， Cef自带的demo也提供了详实的例子参考。

这里除了基本功能外，更多关注在Web端和客户端部分怎么通信，[Cef官方文档](https://bitbucket.org/chromiumembedded/cef/wiki/JavaScriptIntegration.md)也有详细说明。

基本的流程是

    1. OnContextCreate中注入全局函数/对象到V8Context
    2. FunctionHandler中处理js对客户端的函数调用，从renderer进程发送消息到browser进程
    3. browser进程收到调用消息，解析后调用对应C++的api
    4. 结束后将消息发到renderer进程，调用js中的某个全局函数进行回调通知，或调用js传过来的回调函数

可是如果项目里Web页面和客户之间有较多的调用交互，在js和C++之间的通信极其繁琐不便。

代码举例

```C++
    //C++ chrome 渲染进程，这里进行我们的C++ api注入
    void OnContextCreate()
    {
        //inject a very generic function 
        CefRefPtr<CefV8Value> object = getGlobal(...);
        auto func = CefV8Value::CreateFunction(...);
        object->SetValue("callNative", func);
    }

    //Web  js调用客户端api
    windows.callNative("getMyId", arg1, arg2);
    function onNativeResult(apiname, result){
        ...
    }

    //c++ chrome浏览器主进程 这里接收调用消息进行真正的调用
    class ApiObject : public QObject {

        //某个api方法
        //需要检查参数个数和类型
        QVarintMap getMyId(QVariantList arguments)
        {
            if(arguments.size() == 2) {
                if(...){
                    ...
                }
            }
        }

        //某个api方法
        QVarintMap getMyGList(QVariantList arguments);
    }


    //C++  chrome 渲染进程
    //处理我们注入的函数调用，发送到主进程处理
    CefV8Handler::Execute(const CefString& name,
        CefRefPtr<CefV8Value> object,
        const CefV8ValueList& arguments,
        CefRefPtr<CefV8Value>& retval,
        CefString& exception)
    {

    }

    //C++ chrome浏览器主进程 
    //接收函数调用IPC消息，解析，进行真正的调用
    QVariant onJsCall(const QString& apiName, QVariantList arguments)
    {
        //dispath by apiName
        if (apiName == "getMyId")
        {
            return apiObject->getMyId(arguments);
        }
        else if (apiName == "getIdList")
        ....
    }
```

虽然看到了不少程序实际中都是这么做的，但类似这样的实现，稍微有一点小小的不便

1. C++中处理调用的地方，存在对每个api的函数名检查和函数参数的逻辑，每次新增一个api都需要改动，这是一项无甚意义的体力活
2. js对C++的调用比较局限，因为我们期望想使用一个js包一样使用客户端提供的接口，还有支持**事件**，支持**回调函数**，最好支持**promise**

翻翻C#版本的Cef实现可是酷炫多了，也很好解决了上面2个小缺点，其核心便是利用了C#自带的反射功能。

既然用了Qt，那自然应该发挥Qt的能力，其中第一点，首先想到便是利用反射来实现，Qt对C++的反射支持很给力，很容易可以获取一个QObject集成对象的反射信息。

第二点同样使用反射能获取一个Qt的对象的方法和信号，同时利用Cef提供的操作V8对象的方法可以保存V8Function，我们需要做的是监听Qt对象的信号去调用js设置的关联的回调函数。


#

于是在了解了C#版的Cef后，花了两个周末，做了一些改动，以期望最终能达到这样的使用效果

这里的核心是：
* js对C++对象的调用，就像使用用一个js包或window对象一样。

* 客户端注入到js的api，我们只需要把一个继承QObject的对象传入一个特定方法，便完成整个对象的注入工作能在直接js中调用这个对象，其中的注入、解析、调用时的参数检查都能在接入层自动完成。


```C++
    //Web js调用客户端api 以对象形式调用
    window.demoApi.getIdList(id, number, (data) => console.log(data));
    //js监听客户事件(Qt 信号)
    window.demoApi.signalIdChanged.addListener((data) => console.log(data));

    //c++ chrome主进程，某个api对象，就是一个普通的Qt对象
    class DemoApi : public QObject{
    signals:
        void idChanged(QString);
    
    Q_INVOKABLE QVariantMap getIdList(QString id, int number)
        {
            
            ...
        }
    }
    
    //c++ chrome主进程，接收函数调用IPC消息，通过QMetaMethod::invoke进行反射式的调用
    void onJsInvokeMsg(const QString& object, const QString& method, QVariantList arguments)
    {
        QObject* obj;
        QMetaMethod method = find_method(obj, method);
        magic_invoke(method, obj, arguments);
    }

    //C++ chrome主进程，监听某个api对象的信号
    void parseSignals()
    {
        DemoApi* apiObj = ...
        QString signalSignature =  ...
        connect(apiObj, signalSignature, SLOT(onGenericSignal(QObject* , QMetaMethod , QVariantList)))
    }

    //C++ chrome主进程，api对象信号所连接的SLOT方法，将名字和参数打包传到chrome渲染进程，然后调用js注册的回调函数
    void onGenericSignal(QObject* sender, QMetaMethod signal, QVariantList args);
    {
        invokeJsEventCallback(...);
    }

    //我们实现一个方法，可以将一个普通的QObject继承对象注入给js使用
    void injectApiToJavaScript(QObject* apiObject, const QString& name){
        //retriving reflection information and do injecting
    }

    //像这样注入api对象
    DemoApi* apiObj = ...;
    injectApiToJavaScript(apiObj, "demoApi");

```

这里关键需要实现的点

1. **获取Qt对象的反射信息，注入到V8Context中**
2. **js调用C++时，找到对应的Qt对象和方法，并将Cef类型的参数转换成Qt成员方法的参数，通过QMetaMethod::invoke进行调用**
3. **监听Qt对象的信号，Qt使用签名来连接信号槽，不可能匹配所有签名去实现每个SLOT方法， 需要某种方法，可以监听任意签名的信号到同一个SLOT方法中，然后解析出信号名和参数，然后调用js注册的回调函数**

#

看看怎么实现呢

第一点比较简单：

对于一个QObject继承类型，通过它的QMetaObject即可以获取到它的属性，信号，反射方法，然后用Cef提供的V8Context操作接口，创建一个js的V8对象挂到window对象上。

对于Qt的成员方法，创建对应的V8Function设置为我们创建的V8对象的属性。

对于Qt的信号，创建一个新的对象名为信号名字作为上的V8对象的属性，同时对这个新的对象添加addListener和removeListener的方法。

这一段Cef本身的官网和例子已经有相应的实例代码，关键在V8Funtion中我们怎么去响应调用，也就是第二点。

第二点：

对于我们注入到js里的函数，C++通过CefV8Handler::Execute回调接口进行响应

```C++
    bool CefV8Handler::Execute(const CefString& name,
        CefRefPtr<CefV8Value> object,
        const CefV8ValueList& arguments,
        CefRefPtr<CefV8Value>& retval,
        CefString& exception);
```

这里我们可以通过arguments参数的解析 来判断对C++的Qt对象方法的调用是否正确，参数个数和类型是否符合对应的QMetaMethod里保存的信息，然后将调用信息打包传递到browser进程中，在browser进程中去做真正的调用。

browser进程中的响应函数大概长这样，我们需要以反射的方式去调用对象的方法，参数需要一个包装类型，正好有QVariant。

其中arguments是一个QVariant列表，即原js参数列表转换成Qt的类型了，object是对象的注册名，method即方法名。

```C++
    void onJsInvokeMsg(const QString& object, const QString& method, QVariantList arguments);
```

当然有了object名字和method名字，我们很容易找到自己注册的对象和方法（QMetaMethod）。

QMetaMethod的invoke方法，长这样，它需要QGenericArgument作为参数， QGenericReturnArgument作为返回值，通常是这样调用。

```C++
    QMetaMethod::invoke(QObject *object, Qt::ConnectionType connectionType QGenericReturnArgument returnValue, QGenericArgument val0, QGenericArgument val1, ...)

    ...
    QMetaMethod method = metaObject->method(methodIndex);
    method.invoke(obj,
              Qt::DirectConnection,
              Q_RETURN_ARG(QString, retVal),
              Q_ARG(QString, "sqrt"),
              Q_ARG(int, 42),
              Q_ARG(double, 9.7));
```

这里的问题是我们只有QVariant包装的参数，知道其metaType和typeName，但是失去了编译期的静态类型形式，像Q_ARG(QString, "sqrt")这样自然用不了了。

但是我们看一看Q_ARG宏的实现，
```C++
    #define Q_ARG(type, data) QArgument<type >(#type, data)
    #define Q_RETURN_ARG(type, data) QReturnArgument<type >(#type, data)

    template <class T>
    class QArgument: public QGenericArgument
    {
    public:
        inline QArgument(const char *aName, const T &aData)
            : QGenericArgument(aName, static_cast<const void *>(&aData))
            {}
    };

    template <typename T>
    class QReturnArgument: public QGenericReturnArgument
    {
    public:
        inline QReturnArgument(const char *aName, T &aData)
            : QGenericReturnArgument(aName, static_cast<void *>(&aData))
            {}
    };
```
嗯，只需要只要typeName和值的引用（获取地址保存，在异步队列华MetaCall中会拷贝一份）。

这个咱知道啊, QVariant已经提供给我们了
```C++
    class QVariant{
        const char *typeName() const;
        const void *constData() const;
    }
```

于是，于是，爱恨情仇人。。哦不好意思，于是，我们可以这样使用QVariant类型的参数进行metaMehod的调用

```C++
QVariant  metaCallByQVariant(QObject* object, QMetaMethod metaMethod, QVariantList args)
{
    QList<QGenericArgument> arguments;
    for (int i = 0; i < args.size(); i++)
    {
        QVariant& argument = args[i];
        QGenericArgument genericArgument( typeName(argument.typeName(), const_cast<void*>(argument.constData()));
        arguments << genericArgument;
    }

    QVariant res = QVariant((QVariant::Type)metaMethod.returnType(), static_cast<void*>(nullptr));

    QGenericReturnArgument returnArgument(
        res.typeName(),
        const_cast<void*>(res.constData())
    );

    bool ok = metaMethod.invoke(object,Qt::AutoConnection,returnArgument, arguments.value(0), arguments.value(1), arguments.value(2),... arguments.value(9)
        );
    return res;
}
```

第三点，监听Qt对象的信号：

因为我们希望在js中可以监听Qt对象的signal，首先我们可以简化一下，监听一个特定对象特定签名的signal

```C++
    //api对象
    class SomeObject: public QObject {
        ...
        signals:
        void getFxked(QString badguy);
    }

    void injectApi(SomeObject* obj){
        connect(obj, SIGNAL(getFxked(QString)), SLOT(onGetFxked(QString)));
    }

    void onGetFxked(QString badguy) {
        //将对象名，信号名getFxked, 和参数badguy通过Cef的IPC发给渲染进程
    }

    //渲染进程
    void onIpcMessageSignalInvoke(CefValue obj， CefValue signal, CefValue arg) {
        找到保存的监听这个信号的js回调函数，调用
    }

```

但是由于我需要实现对任意一个QObject继承类型的所有可能签名的signal的监听，那现在有没有某个神奇的slot方法去监听任意signal同时获取参数列表和类型形式呢，注意这里是没法用模板的。

```C++
    //no, no idea how to write this
    void someMagicSlot(QString signalName, T1 arg1, T2 arg2, ...);

    //像这样吗
    void someMagicSlot(QString signalName, QvariantList arguments);
```

利用QVariantList似乎是一个可行的方法，毕竟可以接收任何类型和个数的参数了，可是Qt连接signal和slot的时候要求签名匹配，直接connect肯定连不上啊。

这里需要我们看下Qt的MOC是怎么实现signal和slot，我们将mySignal连接到mySlot，然后看下mySlot是怎么被调用的
```C++
signals:
    void mySignal(QString arg1, QString arg2);
public slots:
    void mySlot(QString arg1, QString arg2);

    //moc_myobj.cpp 这里是MOC生成的metecall代码
    void MyObj::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
    {
        if (_c == QMetaObject::InvokeMetaMethod) {
            MyObj *_t = static_cast<MyObj *>(_o);
            Q_UNUSED(_t)
            switch (_id) {
            case 0: _t->mySignal((*reinterpret_cast< QString(*)>(_a[1])),(*reinterpret_cast< QString(*)>(_a[2]))); break;
            case 1: _t->mySlot((*reinterpret_cast< QString(*)>(_a[1])),(*reinterpret_cast< QString(*)>(_a[2]))); break;
            ....
        }
    }
```

可以看到对于所有的metaCall，参数通过一个void** 类型的指针传进来，_a 实际上指向一个数组，这个数组每个值都是一个void指针，其中第0个值执行返回值，其它的执行即执行函数参数。

这里Qt还有一个特性，连接signal和slot时，虽然会检查函数签名，但允许slot的参数个少于signal的参数个数。所以可以将一个任意签名的signal，连接到一个参数为空的slot函数。

但这并没什么用，关键是我们需要在slot函数里拿到真正的参数。

观察moc_myobj.cpp，这个其实就是MyObj的实现的一部分，只不过它是Qt的MOC帮我们生成的，对于任何槽函数的metecall，我们都可以子在qt_static_metacall方法里拦截。

于是，想到一个办法便是，将信号连接到一个参数空的slot **theMagicSlot()**， hook掉qt_static_metacall，将void** 类型的参数_a拿到，调用另一个真正的处理方法 **theRealMagicSlot(void** _a)**。

因为我们拿到了所有的调用参数(void*类型的指针指向参数)，同时我们是知道signal的QMetaMethod的，那么通过signal的QMetaMethod拿到每个参数的类型(QMetaType)，在通过QVariant的构造函数QVariant(int typeId, const void *copy)即可以将每个参数都转换成QVariant。

**Done!** 这个时候，我们知道是哪个信号，当然也知道是哪个对象，也拿到信号的参数，那么便可以将这些信息序列化发到Cef的渲染进程，然后找到监听这个信号的js回调函数，转换参数位CefV8Value类型进行函数调用即可。

```C++
void GenericSignalMapper::theRealMagicSlot(void** _a)
{
    QVariantList args;
    int i = 0;
    foreach(QByteArray typeName, m_method.parameterTypes())
    {
        int type = QMetaType::type(typeName.constData());
        QVariant arg(type, _a[++i]);
        args << arg;
    }

    QObject* obj = sender();
    //现在，我们有了发送对象sender，有信号的MetaMethod，有QVariant包起来的参数
    ...
}
```

当然，hook会引入额外的依赖，实际也不需要Hook。Google一下发现，这个类似的问题也有人问过。只要把MOC生成的moc_xx.cpp文件自己手动修改一下，将其中调用theMagicSlot的那一行代码改成我们的theRealMagicSlot，将_a参数传递进来，然后因为moc_xx.cpp是MOC生成的，我们将修改后的这个文件包含到工程中，同时将这个Qt对象的头文件从工程包含中去掉避免MOC去扫描它，完成！！


除了以上三点，QVariant和CefValue之间的转换，json(QVariantMap)类型处理，js回调函数保存处理，这些都比较简单好实现。

另外，我们实现了以回调形式异步返回结果给JS，但同样我们也可以直接返回Promise给js，而对于客户端某个方法返回QFuture这中本身就是异步形式的api，也可以同AsyncFuture去订阅结果。

具体实现细节和完整的代码请见 [QtCef](https://github.com/hiitiger/QtCef).


# 小结


其实整体没特别需要创造的思路去实现，关键的几个点Google一下就能发现解答，只要了解自己所用的技术，多看看多想想，整合利用好现有的技术，就能很好的的帮助于自己的开发体验和效率。

去年在前一家公司也看到了同样的思路的实现的，当然那位同事厉害多了，实现里模板嵌套类型的检查，当时看完他的宏和模板的嵌套代码令人沉默。

# 最后
那么，思考下如果没有Qt强大的MOC反射系统，现有框架也无力加入一个完整反射系统支持，怎么整呢，是否有办法尽量优化一下我们的重复工作呢？