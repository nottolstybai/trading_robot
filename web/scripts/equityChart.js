function createChart(dayData, monthData){
    function createSimpleSwitcher(items, activeItem, activeItemChangedCallback) {
        var switcherElement = document.createElement('div');
        switcherElement.classList.add('switcher');

        var intervalElements = items.map(function(item) {
            var itemEl = document.createElement('button');
            itemEl.innerText = item;
            itemEl.classList.add('switcher-item');
            itemEl.classList.toggle('switcher-active-item', item === activeItem);
            itemEl.addEventListener('click', function() {
                onItemClicked(item);
            });
            switcherElement.appendChild(itemEl);
            return itemEl;
        });

        function onItemClicked(item) {
            if (item === activeItem) {
                return;
            }

            intervalElements.forEach(function(element, index) {
                element.classList.toggle('switcher-active-item', items[index] === item);
            });

            activeItem = item;

            activeItemChangedCallback(item);
        }

        return switcherElement;
    }

    var intervals = ['Today', 'Month'];

    var seriesesData = new Map([
      ['Today', dayData ],
      ['Month', monthData ],
    ]);

    var switcherElement = createSimpleSwitcher(intervals, intervals[0], syncToInterval);

    var chartBlock = document.getElementById("chart-id");
    var chartElement = document.createElement('div');

    var chart = LightweightCharts.createChart(chartElement, {
        width: chartBlock.offsetWidth,
        height: 400,
        layout: {
            backgroundColor: '#fff',
            textColor: '#000',
        },
        grid: {
            vertLines: {
                color: 'LightGray',
            },
            horzLines: {
                color: 'LightGray',
            },
        },
        rightPriceScale: {
            borderVisible: false,
        },
        timeScale: {
            borderVisible: false,
        },

    });

    chartBlock.appendChild(chartElement);
    chartBlock.appendChild(switcherElement);

    var areaSeries = null;

    function syncToInterval(interval) {
        if (areaSeries) {
            chart.removeSeries(areaSeries);
            areaSeries = null;
        }
        areaSeries = chart.addAreaSeries({
        topColor: 'rgba(76, 175, 80, 0.56)',
        bottomColor: 'rgba(76, 175, 80, 0.04)',
        lineColor: 'rgba(76, 175, 80, 1)',
        lineWidth: 2,
        });
        areaSeries.setData(seriesesData.get(interval));
    }

    syncToInterval(intervals[0]);
}