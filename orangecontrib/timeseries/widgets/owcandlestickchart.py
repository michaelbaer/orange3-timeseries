from PyQt4 import QtCore, QtGui

from datetime import date, datetime, time

from Orange.widgets import widget, gui
from Orange.widgets.highcharts import Highchart
from Orange.data import TimeVariable, Table
from orangecontrib.timeseries import Timeseries

class Highstock(Highchart):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args,
                        highchart='StockChart',
                        rangeSelector_selected=1,
                        title_text='AAPL Historical',
                        **kwargs)
        self.parent = parent

    def addSeries(self, data):

        def ohlcDataMap(x):
            dateString = '{}'.format(x[0])
            date = datetime.strptime(dateString, "%Y-%m-%d").timestamp() * 1000
            open = x[1]
            high = x[2]
            low = x[3]
            close = x[4]
            return [date, open, high, low, close]
        ohlcData = list(map(ohlcDataMap, data))

        def volumeDataMap(x):
            dateString = '{}'.format(x[0])
            date = datetime.strptime(dateString, "%Y-%m-%d").timestamp() * 1000
            volume = x[5]
            return [date, volume]
        volumeData = list(map(volumeDataMap, data))

        groups = [[
                'week',
                [1]
            ], [
                'month',
                [1, 2, 3, 4, 6]
            ]]
        grouping = dict(units=groups)

        yAxesOHLC = dict(labels=dict(align='right',x=-3), title=dict(text='OHLC'), height='60%', lineWidth=2)
        yAxesVolume = dict(labels=dict(align='right',x=-3), title=dict(text='Volume'), top='65%', height='35%', offset=0, lineWidth=2)
        yAxis = [yAxesOHLC, yAxesVolume]

        ohlc = dict(type='candlestick', name='AAPL', dataGrouping=grouping, data=ohlcData)
        volume = dict(type='column', name='Volume', yAxis=1, dataGrouping=grouping, data=volumeData)
        options = dict(series=[], yAxis=yAxis)
        options['series'].append(ohlc)
        options['series'].append(volume)

        self.chart(options)

class OWCandleStickChart(widget.OWWidget):
    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "CandleStick Chart"
    description = "Displays timeseries as candlestick chart."
    icon = 'icons/LineChart.svg'

    inputs = [("Time series", Table, 'set_data')]
    outputs = [("Number", int)]

    def __init__(self):
        super().__init__()
        self.data = None

        self.configsArea = gui.vBox(self.controlArea)
        self.controlArea.layout().addStretch(1)

        self.chart = highstock = Highstock(self, self, debug=True)
        self.mainArea.layout().addWidget(highstock)
        highstock.chart()

    def set_data(self, data):
        self.data = Timeseries.from_data_table(data)
        self.chart.addSeries(data)
