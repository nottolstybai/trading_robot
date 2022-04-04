async function send(){
    selectedStrategy = document.getElementById("select-id").value
    if (selectedStrategy){
        values = selectedStrategy.split("+")
        selectedObj = {
            strategy_id: values[0],
            stock_id: values[1],
            symbol: values[2] 
        }
        console.log(JSON.stringify(selectedObj))
        const rawResponse = await fetch('/api/v1/strategy', {
            method: 'POST',
            headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
            },
            body: JSON.stringify(selectedObj)
        });
        const status = await rawResponse.json();
        console.log(status);
        document.getElementById('popup-content-id').innerHTML = status;
    }
};

async function postSymbol(){
    symbol = document.getElementById("symbol-id").value;
    if (symbol){
        symbolObj = {
            symbol_name: symbol
        };
        console.log(JSON.stringify(symbolObj));
        const rawResponse = await fetch('/api/v1/symbol', {
            method: 'POST',
            headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
            },
            body: JSON.stringify(symbolObj)
        });
        const price = await rawResponse.json();

        console.log(price);

        var priceBlock = document.getElementById("yesterday-price-id")
        var labelBlock = document.getElementById("label-price-id")
        if(price != null){
            priceBlock.innerHTML = price+"$";
            labelBlock.innerHTML = "Market Price";
        }
        else{
            priceBlock.innerHTML = "";
            labelBlock.innerHTML = "";
        }
    }
};

async function postOrderParameters(){
    var selectedOrderType = $("#order-type-id").val();

    var symbol = null;
    var orderType = null;
    var qty = null;
    var tif = null;
    var lmt_price = null;
    var stop_price = null;
    var notional =  null;

    if(selectedOrderType == "market"){
        symbol = document.getElementById('symbol-id').value;
        orderType = "market";
        tif = document.getElementById('tif-id').value;
        if(document.getElementById('dollars-id').checked)
            notional = document.getElementById('qty-id').value;
        else qty = document.getElementById('qty-id').value;
    }
    else if(selectedOrderType == "limit"){
        symbol = document.getElementById('symbol-id').value;
        orderType = "limit"
        tif = document.getElementById('tif-id').value;
        lmt_price = document.getElementById('lmt-price-id').value;
        qty = document.getElementById('qty-id').value;
    }
    else if(selectedOrderType == "stop limit"){
        symbol = document.getElementById('symbol-id').value;
        orderType = "stop limit";
        tif = document.getElementById('tif-id').value;
        lmt_price = document.getElementById('lmt-price-id').value;
        stop_price = document.getElementById('stop-price-id').value;
        qty = document.getElementById('qty-id').value;
    }
    else if(selectedOrderType == "stop"){
        symbol = document.getElementById('symbol-id').value;
        orderType = "stop";
        tif = document.getElementById('tif-id').value;
        stop_price = document.getElementById('stop-price-id').value;
        qty = document.getElementById('qty-id').value;
    }

    orderObj = {
        symbol: symbol,
        order_type: orderType,
        side: "buy",
        notional: notional,
        qty: qty,
        tif: tif,
        lmt_price: lmt_price,
        stop_price: stop_price
    };

    console.log(JSON.stringify(orderObj))

    const rawResponse = await fetch('/api/v1/order', {
        method: 'POST',
        headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        },
        body: JSON.stringify(orderObj)
    });
    const response = await rawResponse.json();
    console.log(response)
    console.log(response)

}

async function postOrderCancel(){
    cancelButton = document.querySelector("#cancel-icon-id")

}