function asyncFunc() {
    return new Promise((resolve, reject) => {
        console.log('asyncFunc')
        resolve('Promise')
    })
}

function callPromise() {
    console.log('callPromise')


    setTimeout(() => {
        console.log('timeout 0')
    }, 0)

    setImmediate(() => {
        console.log('setImmediate')
    })

    asyncFunc().then(r => {
        console.log(`resolve ${r}`)
    })
}


setTimeout(callPromise, 1000)