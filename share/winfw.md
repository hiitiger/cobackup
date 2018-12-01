# Windows 客户端框架小结(Gui)

## 0. 史前时代

以 MFC, WTL为代表的一系列框架，由于工作较晚，参与的项目没有使用这类框架的，现在也没人会再用这类框架去开发有一定规模的项目，简单略过。

#### 开发体验: 比较痛苦，可以进行大量修改减轻痛苦

## 1. 主流时代

以[Qt][1]为首, 各类DirectUI为代表(如[Gaclib][2], [JUCE][3], DuiLib)。
主要特点是DirectUI+面向对象+XML定义UI+强大的布局器(+良好富文本支持)。

这时起，UI业务开发已有体验可言。

典型使用如这样

XML
```xml
    <Window id="xxWindow" title="MyWindow">
        <Button id="xxButton" text="quit" background="close.png">
    </Window>
```

C++
```c++
    xxWindow = CreateFromXml("xx.xml");
    xxButton = xxWindow->GetChildById("xxButton");
```

典型的开发模式是:
1. 有一个新的界面要写，用XML布局，C++搬砖完成UI相关的业务逻辑
2. 有一个新的控件要写，开新Cpp，继承现有基础控件，定义属性，事件，组合某个基础控件，重写各类OnMouseXX/OnKeyXX/OnPaintXX的实现

当然，如果框架支持，也可以做到控件的**自动绑定**，另外可以提供一些**数据绑定**的功能。


工作前2家公司参与的项目正好是使用此类框架为主。

其中第一家是使用Qt，基于其Graphics View做的Gui基础库，提供里XML布局和设计器(貌似没人用)。

第二家是使用公司自研的Gui框架，功能同样强大完整。

然而虽然都能实现需要的功能，但后者使用起来的开发效率和体验却不如前者，这当然有原因是因为Qt本身的强大，也同样有后者自己的一些设计问题，比如动画开发，Qt的属性动画系统要比后者自己开发的动画系统使用灵活舒适。

#### 适用于: 小型软件，大型软件，性能要求，体积要求，复杂的自定义UI要求等
#### 开发体验: 取决于框架设计本身，大部分时候都是搬砖的体验

#### 推荐开源项目:
* [Telegram][4] 基于Qt的Telegram客户端
* [Gaclib][2], [JUCE][3] 设计极佳，相比Qt代码量不大，非常适合学习，有不少产品应用


## 2. 客户端新时代

以[Qt Quick(Qt Qml)][5], [迅雷bolt][6]为代表。

典型的特点框架本身提供原子控件，基于原子控件组合来创建新控件，**脚本化界面逻辑**。

bolt个人没怎么用过，前几年在一个项目中曾基于Qt Qml开发了一套基础UI库。

Qml是Qt为以新一代Gui系统开发的语言，类json的语法，js支持，本身脚本引擎提供的context注入，强大的属性绑定，动画(这些也依赖Qt本身的元对象系统)。

从此时开发，UI开发的体验可以用爽来形容了。

Label和MouseArea组合生成新的Button控件

```qml
    FancyButton {
        property alias text: label.text
        signal clicked(real x, real y)
        Label{
            id: label
        }

        MouseArea{
            onClicked: {
                console.log("button clocked")
                parent.clicked(mouse.x, mouse.y)
            }
        }
    }
```

Qml相比于其它类似框架的优势，在于Qml语言本身设计简洁，自带JS引擎提供里很多有用的语法糖，js的支持也很好上手，再加上Qt本身的强大集成库。

当然，鉴于Qml的强大，也可以在Qml里面完成你的业务逻辑，甚至用C++写UI，Qml写逻辑也行。

#### 开发体验: 可以用爽来形容了
#### 适用于: UI业务变化多，体积限制不大，想要提高UI开发的效率
#### 推荐开源项目: [qml-material][7], 这个项目很久没跟新了，不过可以看看用QML来开发UI控件是怎样的

## 3. Web混合框架时代

这里可以分为[Cef][8]为代表的和[electron][9]为代表的。

这时界面开发，以Web为主，根据需要，部分逻辑由native代码来实现。

最近的两个项目中都是基于Cef的。

使用此类框架，其实对开发本身提出里技术广度更高的要求。如果native和web部分割裂开发，分别开发，就不能完全利用这类框架的优点。

Cef(包括Qt WebEngine)对比electron(nw.js)的特点是，可以同时拥有更完整的native能力，比如可以同时使用某些native的UI库。

这里个人比较喜欢的是electron，见到大部分用Cef开发的软件其实都可以用electron来发，当然这会在native能力上受到一定的约束。但TypeScript+nodejs的开发效率可比C++翻倍了还多啊。

Cef类比较有名的产品如EA Origin(Qt WebEngine), Steam(Cef)等。

electron类比较有名的产品有VS Code, discord等。

#### 开发体验: ❤ TypeScript
#### 适用于:
* UI业务变化多，体积限制不大，想要提高UI开发的效率
* IM类，工具类，Web跨平台
#### 推荐开源项目:
* [vs code][10], [streamlabs-obs][11]
* [OverWolf][12]，基于Cef的，并不是开源软件，但是C#写的可以反编译看源码

# note
WPF, PyQt not inlcuded

[1]: https://www.qt.io/
[2]: http://gaclib.net/
[3]: https://juce.com/
[4]: https://github.com/telegramdesktop/tdesktop
[5]: https://doc.qt.io/qt-5.11/qtquick-index.html
[6]: http://bolt.xunlei.com/
[7]: https://github.com/papyros/qml-material
[8]: https://bitbucket.org/chromiumembedded/cef
[9]: https://electronjs.org/
[10]: https://github.com/Microsoft/vscode
[11]: https://github.com/stream-labs/streamlabs-obs
[12]: https://www.overwolf.com/