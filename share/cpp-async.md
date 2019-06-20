# uncool C++ - make async cool again

这是我们C++使用中经常遇到的一个小问题，异步调用和回调。

## preview
```C++
    auto t = delayed(1000)
    | ui([] {
        std::cout << "running on ui" << std::endl;
    })
    | pool([] {
        std::cout << "running on pool" << std::endl;
        return std::this_thread::get_id();
    })
    | delay<std::thread::id>(100)
    | pool([](std::thread::id id) {
        std::cout << "running on pool" << std::endl;
        std::cout << "received thread_id" << id  << std::endl;
    });
```

## 正文，其实是引言

假设我们业务有个小需求，需要读取本地一个文件，拿到一个参数，然后请求一个服务获取数据。

如果就像这样，我们一眼就看明白它的逻辑
```JavaScript
    function getDataFromRemote(){
        fs.readFile("myfile.text", "utf-8")
        .then((hashId) => {
            return fetch(`https://myapp.local/api/data?id=${hashId}`)
        })
        .then((reponse) => {
            return reponse.json();
        })
        .then((datas) => {
            console.log(datas)
        })
    }
```


那么对于用C++开发的我们经历了什么呢。

由于HTTP请求需要较长时间，肯定不能卡我们的UI线程，我们怎么做的呢。

#### 开线程 + 发消息 

这大概是1999年的风格？

```C++
    void ReadTextFile(const char* filename, void* buffer, ...);
    HTTPResponse HttpQuery(const char* url, ...);

    #define WM_QUERY_DATA_RES WM_USER+123

    DWORD __stdcall QueryDataFromRemote(LPVOID lpThreadParameter)
    {
        CHAR* url[1024];
        GetUrl(url, (const char*)lpThreadParameter);
        HTTPResponse res = HttpQuery((const char*)url, ...);
        JsonResult* pJson = XXParseJson(res.data);
        PostMessage(xguiWindow, WM_QUERY_DATA_RES, pJson, 0);
        free(lpThreadParameter);
        return 0;
    }

    void MyFunc()
    {
        void* buffer;
        ReadTextFile("myfile.txt", (LPVOID)buffer, ...);
        CreateThread(0, 0, QueryDataFromRemote, buffer, 0, 0);
    }

    void XGuiWindowProc(UINT uMsg, WPARAM wParam, ...)
    {
        if (wMsg == WM_QUERY_DATA_RES)
        {
            JsonResult* pJson = (JsonResult*)wParam;
            ...
        }
    }

```
额，有点头大，一个异步的逻辑链条调试追踪很不容易啊，而且发消息还是弱类型。


#### 开线程 + callback函数

这大概也是1999年的风格？

```C++
    std::string ReadTextFile(const std::string filename,...);
    HTTPResponse HttpQuery(const std::string url, ...);

    void QueryDataFromRemote(void *lpThreadParameter)
    {
        HTTPCallRet* p = (HTTPCallRet*)lpThreadParameter;
        std::string url = GetUrl(p->hasdId);
        HTTPResponse res = HttpQuery(url, ...);
        JsonResult* jsonRes = XXParseJson(res.data);
        p->OnMyData(jsonRes);
        return 0;
    }

    void OnMyData(JsonResult* datas)
    {
        //
    }

    void MyFunc()
    {
        std::string hasdId = ReadTextFile("myfile.txt",  ...);

        HTTPCallRet* p = new HTTPCallRet(hashId, OnMyData);
        CreateThread(0, 0, QueryDataFromRemote_, buffer, 0, 0);
    }

```
并没有实质改进，回调函数可能比消息处理稍好一点，但是回调结果切到UI还是要走会PostMessage？

#### 多线程任务队列 + post custom bind function

到2000年了

```C++
    void QueryDataFromRemote(const std::string& hasdId, CallBackFn OnMyData) {
        std::string url = GetUrl(hasdId);
        HTTPResponse res = HttpQuery(url, ...);
        JsonResult jsonRes = XXParseJson(res.data);
        PostFunction(UI_THREAD, OnMyData, jsonRes);
    }

    void OnMyData(const JsonResult& datas);

    void MyFunc()
    {
        std::string hasdId = ReadTextFile("myfile.txt",  ...);
        PostFunction(IO_THREAD, QueryDataFromRemote, hasdId, OnMyData);
    }
```

这时逻辑看起来清晰了，这也是Chrome里大量使用的方式。但是如果异步逻辑链条很长呢？

C++11 里终于有了lambda，同时还有async，这样似乎更清楚一些。
```C++
    void OnMyData(const JsonResult& datas);

    void QueryDataFromRemote()
    {
        std::string hasdId = GetHasdId(...);
        std::async([hasdId]() {
            std::string url = GetUrl(hasdId);
            HTTPResponse res = HttpQuery(url, ...);
            JsonResult jsonRes = XXParseJson(res.data);
            framework::async(OnMyData, jsonRes);
        });
    }

```

可是很快我们便陷入callback hell。

``` C++
    void some_async_func(SucceedCallBack callback) {
        std::async([callback]() {
            if (xxx) {
                std::async([callback]() {
                    if (yyy) {
                        std::async([callback]() {
                            if (zzz) {
                                callback();
                            }
                        });
                    }
                    else {
                        callback();
                    }
                });
            }
            else {
                callback();
            }
        });
    }
```

#### promise like

201x年代了，C++也要与时俱进了，来个promise风格

```C++
    void OnMyData(const JsonResult& datas);

    concurrency::task<void> QueryDataFromRemote() {
        return concurrency::create_task([]() {
                    std::string hasdId = GetHasdId();
                    return hasdId;
                }).then([](const std::string& hasdId) {
                    std::string url = GetUrl(hasdId);
                    HTTPResponse res = HttpQuery(url);
                    JsonResult jsonRes = XXParseJson(res.data);
                    return jsonRes;
                }).then(OnMyData);
    }
```

当然，C++不仅有了promise风格库，还有了协程。
```C++
    concurrency::task<void> QueryDataFromRemote() {
        std::string hashId = co_await readHasdId();
        JsonResult jsonRes = co_await queryRemoteJson(hashId);
        OnMyData(jsonRes);
    }

```

到此，我们终于用上了await了，但是还需注意协程使用里的小坑😋。

#### BUT
还有一个问题，在C++里使用promise或者await，我们要怎么指定then后面的内容在什么线程里运行呢？

```C++
    concurrency::task<bool>  FXKCls::init()
    {
        using namespace concurrency_;
        __await (_loadConfigFromFile() && _loadDataFromFile());
        __awaitui _analyzeData();

        m_ready = true;

        delayed(3000)
            | pool ([this](){
                startWatch();
            })
            | delay(30000)
            | ui([this](){
                return getRId();
            })
            | http ([this](std::string param) {
                _fetchRemoteUpdate(param);
            });

        __return m_ready;
    }
```

[more async](https://github.com/hiitiger/CoolerCppIdiom#ppl-async-adapter)。

