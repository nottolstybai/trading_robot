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
        const rawResponse = await fetch('/api/strategies', {
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