# Windbg dump分析使用简介
	  http://windbg.info/download/doc/pdf/WinDbg_A_to_Z_bw2.pdf
	  http://www.yiiyee.cn/Blog/windbg/
	 《软件调试》

1.	安装和配置
	* 可以通过Windows SDK安装或者单独安装包安装
	* 配置符号文件： srv\*D:\tmp\pdb\*http://msdl.microsoft.com/download/symbols;D:\other\path

2.	 帮助
	* 通过 .hh指令或者F1打开帮助文档

3.	指令类型
	* 常规指令，控制被调试程序: kv, g, lm, dds等
	* 元指令，控制调试器: .sympath, .cls
	* 扩展指令: !anlayze, !teb, !handle

4.	定位错误
	* .ecxr 指令 定位到当前异常的上下文
	* !anlayze -v 可以让调试器自动分析得到基本的异常信息

5. 	堆栈回溯
	 * kv 显示堆栈
	 * 定位到异常时，调试器即会显示堆栈信息，但有时调用栈已不对
	 *  dds esp/ dds ebp 打印堆栈上的符号，然后进行手工回溯，
	 * 如果esp, ebp已经被破坏，通过!teb 指令 获取线程的esp和ebp
	 * 回溯成功后kv=ebp esp 来查看堆栈

6. 	堆栈操作
	* kv, kv=ebp esp
	* ~ 切换线程
	* ~*kv 显示所有线程堆栈
	* !uniquestack 显示所有线程堆栈，但会提出相同的重复线程
	* .frame切换栈帧

7.	查看内存
	* d*
	* 查看局部变量 dv minidump下基本只能看到一层树
	* 按类型显示变量 dt
	* 查看寄存器 r
	*  搜索内存 S -d [Range] [Pattern]
	* 查字符串 dpa，dpu
	* 解引用指针 dpp
	* 查看链表 dl

8. 查看符号
	* ln [addr] 显示指定地址附件的符号
	* dds [Range] 显示给定范围内的内容，会显示相关的符号信息
	* dpp, dps
	* x module!symbol, 查看某个模块的符号

9. 模块
	* lm, lmvm
	* 加载模块符号 .reload
	*  通过.reload /f /i pdbfilepath=Addr, 强行将pdb文件load到Addr地址， Addr应该是没有被其他模块占用的地址
	* !sym noisy, reload /f /o

10. 搜索this指针
	* 搜索模块符号， 可以用来通过搜索虚函数地址来搜索对象的地址this指针
	* x Module!ClassName::*vftable* --> vtbale_address
	* s -d [range] vtbale_address

11. 调试堆破坏(fulldump)
	* !heap -v [heap], 检查堆
	* !heap -i [address],  获取address的信息
	* !heap -flt s [size], 列出大小为size的heap堆块
	* !heap -stat -h [handle], 统计堆的使用信息
	* !heap -x [address], 搜索包含address的堆块

12. 内存泄漏(fulldump)
	* !heap -s 堆使用统计信息
	* !heap -stat -h [handle], 查看某个堆的使用信息
	* !heap -flt s [size], 列出大小为size的heap堆块
	* d* 查看内存

13. 其它一些常见问题和方法

	1.  堆破坏的问题，只看minidump 无法解决，需要使用debug allocator 如crtdbg.h 或 开页堆

	2. 有时候加载了不同版本的CRT，这是因为在程序启动后，又安装了VCRT库，然后新load的DLL可能会加载到新版本的CRT, 可以去掉manifest文件使所有的DLL都直接使用同一份CRT 或者 放一份CRT在自己的目录下

	3. appverify，可以用来检测各种问题。添加程序，选择要测试的项目，设置默认的调试器，这样在程序启动后，出现错误时会启动调试器
	4.  Memory corruption
     	* 原因： 写入非法内存地址     
     	* 分析步骤 ：状态分析，源码中寻找可能的出错路径，通过对写入的内存数据分析缩小猜测范围
	5.  特权指令
     	* 指令被破坏; 指令不对齐,内存与二进制文件不符.这都是非代码问题.
     	* 跳到了一个错误地址,比如对象释放,调用了虚函数.代码问题
	6.  EIP指令被篡改
    	* 函数入口点附近, x  查看是否执行文件在内存中被修改了，可能是被inline hook 修改了函数入口处的指令
	7.  NX_FAULT
     	* 有些程序调用了virtualprotect，在恢复前执行到这里了。
	8.  堆栈溢出
     	* kv 0xffff 查看堆栈
	9.  在发生重入导致crash的时候，kv看不到上面的堆栈，如果猜测可能有重入问题，dds一下esp上面一段，查找代码定位
	10. 如果dump自动分析出现的异常是Break instruction exception, 记得查看所有线程的堆栈，因为可能出现多线程异常
	11. 优化的代码
    	*  有时候函数内部会使用栈上存放入参的地址来复用，这时候windbg里堆栈显示结果的参数信息就不准确了
    	*  OMAP优化
			here is another  compiler  optimization  we  should  be aware  of  and  it  is  called OMAP  (page 294). It moves the  code  inside  the  code  section and  puts  the  most  fre-quently accessed code fragments together