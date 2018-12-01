# Memory management in C++

### RAII
    * std::unique_ptr, scoped_ptr
    * hanlde class

### reference couting smart ptr
    * ComPtr
    * std::shared_ptr

### weak ptr
    * weak ptr based on reference counting, std::weak_ptr 
    * object ptr based on object guarding, QPointer in Qt, TWeakObjectPtr in UE4

### implicit shared data
    * copy on write

### delayed delete
    * this->deleteLater instead of delete this

### object tree
    * in some UI control tree mamagement