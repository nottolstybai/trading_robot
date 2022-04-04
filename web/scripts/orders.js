function updateSubmitOrderForm(){
    orderType = $("#order-type-id").val()
    if(orderType == "limit") {
        $("#changable-black-id").html(`
            <label>Limit Price</label>
            <input id="lmt-price-id" type="number" name="limit-price" step="0.01">
        `);
    }
    else if(orderType == "stop") {
        $("#changable-black-id").html(`
            <label>Stop Price</label>
            <input id="stop-price-id" type="number" name="stop-price" step="0.01">
        `);
    }
    else if(orderType == "stop limit") {
        $("#changable-black-id").html(`
            <div class="ui fields">
                <div class="field">
                    <label>Limit Price</label>
                    <input id="lmt-price-id" type="number" name="limit-price" step="0.01">
                </div>
                <div class="field">
                    <label>Stop price</label>
                    <input id="stop-price-id" type="number" name="stop-price" step="0.01">
                </div>
            </div>
        `);
    }
    else if(orderType == "market") {
        $("#changable-black-id").html(`
            <label>Choose how to buy</label>
            <div class="ui fields">
                <div class="field">
                    <div class="ui checkbox">
                        <input id="dollars-id" type="checkbox" name="payment-method">
                        <label>Buy as dollars</label>
                    </div>
                </div>
            </div>
        `);
    }
}

function runUpdateFunc(){
    document.onload = updateSubmitOrderForm();
    var orderTypeSelector = document.getElementById('order-type-id');
    orderTypeSelector.addEventListener('change', updateSubmitOrderForm);
}