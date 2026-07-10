function addWorker(worker){
    if(typeof window.WORKERS_ARR == 'undefined'){
        window.WORKERS_ARR = {};
    }

    window.WORKERS_ARR[worker.name] = {
        worker: new Worker(document.currentScript.src.replaceAll('worker.js', worker.url)),
        callbacksArr: {},
        init: function(){
            window.WORKERS_ARR[worker.name].worker.onmessage = (event) => {
                const { requestId, responseData } = event.data;
                if(Object.prototype.hasOwnProperty.call(window.WORKERS_ARR[worker.name].callbacksArr, requestId)){
                    window.WORKERS_ARR[worker.name].callbacksArr[requestId](responseData);
                    delete window.WORKERS_ARR[worker.name].callbacksArr[requestId];
                }
            };
        },
        generateUUID: function() {
            var d = new Date().getTime();
            var d2 = ((typeof performance !== 'undefined') && performance.now && (performance.now()*1000)) || 0;
            return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                var r = Math.random() * 16;
                if(d > 0){
                    r = (d + r)%16 | 0;
                    d = Math.floor(d/16);
                } else {
                    r = (d2 + r)%16 | 0;
                    d2 = Math.floor(d2/16);
                }
                return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
            }).split('-').join('');
        },
        call: function(handlerData, callback){
            let callbackId = window.WORKERS_ARR[worker.name].generateUUID();
            
            if(typeof callback == 'function'){
                window.WORKERS_ARR[worker.name].callbacksArr[callbackId] = callback;
            }
    
            window.WORKERS_ARR[worker.name].worker.postMessage({ 
                requestId: callbackId, 
                requestData: typeof handlerData != 'undefined' ? handlerData : {}
            });
        }
    }

    window.WORKERS_ARR[worker.name].init();
}

addWorker({
    name: "HTTP_WORKER",
    url: 'http-worker-v1.js'
});