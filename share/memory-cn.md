# C++里的资源/内存管理

作为用了一段时间的入门 C++开发者，自己感觉到这们语言最重要的特性或者唯一还能让人觉得不错的特性就是确定性析构了（当然，如果可以不用 C++ 才是最好的）。

C++的世界里，内存/资源相关的问题一直是个大麻烦，我们可以精确的控制资源的分配和释放，但同时内存/资源泄漏，use after free，内存破坏等等问题也很烦人。

内存/资源泄漏似乎是最常见的，也是没有 GC 语言的一大痛苦。

```C++
    void tryFxkCpp() {
        File* fxkFile = new File("fxk.cpp");
        try {
            if (!fxkFile->open(File::ReadWrite)) {
                delete fxk;
                return;
            }
            fxkFile->write("Hello!");
        }
        catch(std::exception& e) {
            delete fxk;
            return;
        }
        // oops - forget to delete fxk
    }
```

当然我们生活在 C++的世界，我们的类型都有析构函数，我们的变量有其确定作用域，离开作用域，编译器会保证生成正确的代码帮我们释放作用域上的变量。

利用此特性，C++里最基础也是所有内存管理的根本方式既是 RAII， 资源获取既初始化。

## RAII

-   大括号作用域，确定性析构
-   std::unique_ptr, scoped_ptr 等职能指针
-   句柄类

```C++
     void tryFxkCpp() {
        std::unique_ptr<File> = std::make_unique<File>("fxk.cpp");
        try {
            if (!fxkFile->open(File::ReadWrite)) {
                return;
            }
            fxkFile->write("Hello!");
        }
        catch(std::exception& e) {
        }
    }
```

基于此，为了夸作用域的对象生存，又不用回到老式的手动管理

## 引用计数智能指针

-   std::shared_ptr，CComPtr(Windows), scoped_refptr(Chrome)
-   std::weak_ptr

其中引入了**弱指针**，是为了不对某个对象加以强引用，但是在后面某个时刻会根据对象是否依然存在做一些逻辑处理的时候用到。

```C++
    void tryFxkCpp() {
        std::shared_ptr<Fxker> fxker = std::make_shared<Fxker>("fxkcpp");
        fxker->do_some_thing();
        framework::async([weak_fxker = fxker->weak_from_self()](){
            if(auto fxker = weak_fxker.lock()) {
                fxker->do_some_other_thing();
            }
        } );
    }
```

弱指针除了基于引用计数的，还有其它实现，如经典的 QPointer

-   QPointer (Qt)
-   TWeakObjectPtr (UE4)

```C++
    MyWidget* tipWidget = getTipWidget();
    QPointer<QWidget> tipWidgetPtr = tipWidget;

    this->my_button_clicked().add([tipWidgetPtr]() {
        if (tipWidgetPtr) {
            tipWidgetPtr->animteOut();
        }
    });
```

当然，如果只有这些方式肯定还不够，经典的 copy on write 在 C++里也是十分容易实现的

## COW (隐式数据共享)

```C++
template <class T>
class CowPtr
{
    public:
        typedef std::shared_ptr<T> RefPtr;

    private:
        RefPtr m_sp;

        void detach()
        {
            T* tmp = m_sp.get();
            if( !( tmp == 0 || m_sp.unique() ) ) {
                m_sp = RefPtr( new T( *tmp ) );
            }
        }

    public:
        CowPtr(T* t)
            :   m_sp(t)
        {}
        CowPtr(const RefPtr& refptr)
            :   m_sp(refptr)
        {}
        const T& operator*() const
        {
            return *m_sp;
        }
        T& operator*()
        {
            detach();
            return *m_sp;
        }
        const T* operator->() const
        {
            return m_sp.operator->();
        }
        T* operator->()
        {
            detach();
            return m_sp.operator->();
        }
};
```

似乎只有这些方式还不够啊，记得在不少 GUI 程序里见到过管理 UI 对象都采用引用计数管理，每次都让人头大，明明在窗口销毁时，其上的控件都应该被销毁啊。

嗯，这种方式就是对象树了

## 对象树

-   父对象析构时，会销毁子对象
-   Gui 控件树，程序逻辑对象等

最后，`delete this` 这种东西相信大家也没少见，可是其容易引起错误也很难受呀，那么干脆做成异步好了

## delete later

-   对象自己销毁自己，但是是异步的，避免 delete this 的常见问题

```C++
    class TObject
    {
        deleteLater() {
            auto weakSelf = TWeakPtr<TObject>(this);
            framework::async([weakSelf]() {
                if (weakSelf) {
                    delete weakSelf.get();
                }
            });
        }
    }
```

## 总结下

-   RAII

    -   std::unique_ptr, scoped_ptr
    -   hanlde class

-   reference couting smart ptr

    -   std::shared_ptr, scoped_refptr

-   weak ptr

    -   weak ptr based on reference counting, std::weak_ptr
    -   object ptr based on object guarding, QPointer in Qt, TWeakObjectPtr in UE4

-   implicit shared data

    -   copy on write

-   delayed delete

    -   `this->deleteLater` instead of `delete this`

-   object tree
    -   parent object manages its childrens
