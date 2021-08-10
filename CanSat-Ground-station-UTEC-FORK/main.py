from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
from communication import Communication
import math
from dataBase import data_base
import sys
import io
from PyQt5.QtWidgets import QPushButton, QApplication, QWidget, QHBoxLayout, QVBoxLayout
import folium
from PyQt5.QtWebEngineWidgets import QWebEngineView
import io
from datetime import datetime

pg.setConfigOption('background', (33, 33, 33))
pg.setConfigOption('foreground', (197, 198, 199))
# Interface variables
app = QtGui.QApplication([])
view = pg.GraphicsView()
Layout = pg.GraphicsLayout()
view.setCentralItem(Layout)
view.show()
view.setWindowTitle('CanSat Flight monitoring')
view.resize(1200, 700)

# declare object for serial Communication
ser = Communication()
# declare object for storage in CSV
data_base = data_base()
# Fonts for text items
font = QtGui.QFont()
font.setPixelSize(90)

# Title at top
text = """
Flight monitoring interface for cansats and OBC's <br>
developed at the Universidad Distrital FJC. <br>
Modified for UTEC PI3 Cansat Project.
"""
Layout.addLabel(text, col=1, colspan=21)
Layout.nextRow()

# Put vertical label on left side
Layout.addLabel('LIDER - ATL research hotbed',
                angle=-90, rowspan=3)

Layout.nextRow()
# Save data buttons

# buttons style
style = "background-color:rgb(37, 150, 190);color:rgb(0,0,0);font-size:14px;"

lb = Layout.addLayout(colspan=21)
proxy = QtGui.QGraphicsProxyWidget()
save_button = QtGui.QPushButton('Start storage')
save_button.setStyleSheet(style)
save_button.clicked.connect(data_base.start)
proxy.setWidget(save_button)
lb.addItem(proxy)
lb.nextCol()


proxy2 = QtGui.QGraphicsProxyWidget()
end_save_button = QtGui.QPushButton('Stop storage')
end_save_button.setStyleSheet(style)
end_save_button.clicked.connect(data_base.stop)
proxy2.setWidget(end_save_button)
lb.addItem(proxy2)


Layout.nextRow()

# Altitude graph
l1 = Layout.addLayout(colspan=20, rowspan=2)
l11 = l1.addLayout(rowspan=1, border=(83, 83, 83))
p1 = l11.addPlot(title="Altitude (m)")
altitude_plot = p1.plot(pen=(29, 185, 84))
altitude_data = np.linspace(0, 0, 30)
ptr1 = 0


def update_altitude(value_chain):
    global altitude_plot, altitude_data,  ptr1
    altitude_data[:-1] = altitude_data[1:]
    altitude_data[-1] = float(value_chain[4])
    ptr1 += 1
    altitude_plot.setData(altitude_data)
    altitude_plot.setPos(ptr1, 0)


# Speed graph
p2 = l11.addPlot(title="Speed (knots)")
vel_plot = p2.plot(pen=(29, 185, 84))
vel_data = np.linspace(0, 0, 30)
ptr6 = 0
vel = 0


def update_vel(value_chain):
    global vel_plot, vel_data, ptr6, vel
    vel = value_chain[2]
    vel_data[:-1] = vel_data[1:]
    vel_data[-1] = vel
    ptr6 += 1
    vel_plot.setData(vel_data)
    vel_plot.setPos(ptr6, 0)

coordinate = (-12.135400, -77.022095) # STARTING ADDRESS #(37.819859404476425, -122.47855046471037)

m = folium.Map(
    title='cansat',
    zoom_start=18,
    location=coordinate
)

data = io.BytesIO()
m.save(data, close_file=False)
webView = QWebEngineView()
webView.setHtml(data.getvalue().decode())

proxy3 = QtGui.QGraphicsProxyWidget()
proxy3.setWidget(webView)
proxy3.update()
count = 0

W3 = l11.addItem(proxy3)
lat = 0
lon = 0

def update_MAP(value_chain):
    global proxy3,m,data,W3,webView,l11,data,count,lat,lon

    loc = []
    if (lat == 0):
        loc = [ (float(value_chain[1]), float(value_chain[0])),
                (float(value_chain[1]), float(value_chain[0]))]
    else:
        loc = [ (lat, lon),
                (float(value_chain[1]), float(value_chain[0]))]
    lat = float(value_chain[1])
    lon = float(value_chain[0])
    m.location = (lat,lon)


    folium.PolyLine(loc,
                color='red',
                weight=15,
                opacity=0.8).add_to(m)

    if count == 20:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        folium.Marker(
            [float(value_chain[1]), float(value_chain[0])], 
            popup = str(float(value_chain[1])) + ',' + str(float(value_chain[0])) + '\n' + dt_string,
            icon=folium.Icon(color='blue',icon="fab fa-fly",prefix='fa'),
            tooltip="GPS SIGNAL"
        ).add_to(m)

    data2 = io.BytesIO()
    m.save(data2, close_file=False)
    m.save('trayectoria.html')
    if count == 20:
        webView.setHtml(data2.getvalue().decode())
        count = 0
    else:
        count+=1
        print(count)

l1.nextRow()
l12 = l1.addLayout(rowspan=1, border=(83, 83, 83))

# Acceleration graph
acc_graph = l12.addPlot(title="Accelerations (m/s²)")
# adding legend
acc_graph.addLegend()
acc_graph.hideAxis('bottom')
accX_plot = acc_graph.plot(pen=(102, 252, 241), name="X")
accY_plot = acc_graph.plot(pen=(29, 185, 84), name="Y")
accZ_plot = acc_graph.plot(pen=(203, 45, 111), name="Z")

accX_data = np.linspace(0, 0)
accY_data = np.linspace(0, 0)
accZ_data = np.linspace(0, 0)
ptr2 = 0


def update_acc(value_chain):
    global accX_plot, accY_plot, accZ_plot, accX_data, accY_data, accZ_data, ptr2
    accX_data[:-1] = accX_data[1:]
    accY_data[:-1] = accY_data[1:]
    accZ_data[:-1] = accZ_data[1:]

    accX_data[-1] = float(value_chain[10])
    accY_data[-1] = float(value_chain[11])
    accZ_data[-1] = float(value_chain[12])
    ptr2 += 1

    accX_plot.setData(accX_data)
    accY_plot.setData(accY_data)
    accZ_plot.setData(accZ_data)

    accX_plot.setPos(ptr2, 0)
    accY_plot.setPos(ptr2, 0)
    accZ_plot.setPos(ptr2, 0)


# Gyro graph
gyro_graph = l12.addPlot(title="Gyro")
gyro_graph.hideAxis('bottom')
# adding legend
gyro_graph.addLegend()
pitch_plot = gyro_graph.plot(pen=(102, 252, 241), name="Pitch")
roll_plot = gyro_graph.plot(pen=(29, 185, 84), name="Roll")
yaw_plot = gyro_graph.plot(pen=(203, 45, 111), name="Yaw")

pitch_data = np.linspace(0, 0)
roll_data = np.linspace(0, 0)
yaw_data = np.linspace(0, 0)
ptr3 = 0


def update_gyro(value_chain):
    global pitch_plot, roll_plot, yaw_plot, pitch_data, roll_data, yaw_data, ptr3
    pitch_data[:-1] = pitch_data[1:]
    roll_data[:-1] = roll_data[1:]
    yaw_data[:-1] = yaw_data[1:]

    pitch_data[-1] = float(value_chain[7])
    roll_data[-1] = float(value_chain[8])
    yaw_data[-1] = float(value_chain[9])

    ptr3 += 1

    pitch_plot.setData(pitch_data)
    roll_plot.setData(roll_data)
    yaw_plot.setData(yaw_data)

    pitch_plot.setPos(ptr3, 0)
    roll_plot.setPos(ptr3, 0)
    yaw_plot.setPos(ptr3, 0)


# Humidity Graph
humidity_graph = l12.addPlot(title="Humidity")
humidity_plot = humidity_graph.plot(pen=(102, 252, 241))
humidity_data = np.linspace(0, 0, 100)
ptr5 = 0

def update_humidity(value_chain):
    global humidity_plot, humidity_data,  ptr5
    humidity_data[:-1] = humidity_data[1:]
    humidity_data[-1] = float(value_chain[6]) 
    ptr5 += 1
    humidity_plot.setData(humidity_data)
    humidity_plot.setPos(ptr5, 0)

# Pressure Graph
pressure_graph = l12.addPlot(title="Barometric pressure")
pressure_plot = pressure_graph.plot(pen=(102, 252, 241))
pressure_data = np.linspace(0, 0, 30)
ptr4 = 0

def update_pressure(value_chain):
    global pressure_plot, pressure_data,  ptr4
    pressure_data[:-1] = pressure_data[1:]
    pressure_data[-1] = float(value_chain[5])
    ptr4 += 1
    pressure_plot.setData(pressure_data)
    pressure_plot.setPos(ptr4, 0)


# Temperature graph
graf_temp = l12.addPlot(title="Temperature (ºc)")
temp_plot = graf_temp.plot(pen=(29, 185, 84))
temp_data = np.linspace(0, 0, 30)
ptr5 = 0


def update_temp(value_chain):
    global temp_plot, temp_data,  ptr5
    temp_data[:-1] = temp_data[1:]
    temp_data[-1] = float(value_chain[3])
    ptr5 += 1
    temp_plot.setData(temp_data)
    temp_plot.setPos(ptr5, 0)


# PARACHUTE - CAMERA - TRANSMITTER - CONTROL

l2 = Layout.addLayout(border=(83, 83, 83))

# transmitter graph
transmitter_graph = l2.addPlot(title="Transmitter satus")
transmitter_graph.hideAxis('bottom')
transmitter_graph.hideAxis('left')

def update_transmitter(value_chain):
    global transmitter_graph
    if value_chain[15] == 1:
        transmitter_text1 = pg.TextItem("CONNECTED", anchor=(0.5, 0.5), color="g")
        transmitter_text1.setFont(font)
        transmitter_graph.addItem(transmitter_text1)
    else:
        transmitter_text1 = pg.TextItem("NO SIGNAL", anchor=(0.5, 0.5), color="r")
        transmitter_text1.setFont(font)
        transmitter_graph.addItem(transmitter_text1)


l2.nextRow()

# camera graph
camera_graph = l2.addPlot(title="Camera satus")
camera_graph.hideAxis('bottom')
camera_graph.hideAxis('left')

def update_camera(value_chain):
    global camera_graph
    if value_chain[14] == 1:
        camera_text1= pg.TextItem("PASS", anchor=(0.5, 0.5), color="g")
        camera_text1.setFont(font)
        camera_graph.addItem(camera_text1)
    else:
        camera_text1= pg.TextItem("FAIL", anchor=(0.5, 0.5), color="r")
        camera_text1.setFont(font)
        camera_graph.addItem(camera_text1)


l2.nextRow()

parachute_status_graph = l2.addPlot(title="Parachute deployed")
parachute_status_graph.hideAxis('bottom')
parachute_status_graph.hideAxis('left')

def update_parachute(value_chain):
    global parachute_status_graph
    if(value_chain[13] == 0):
        parachute_status_text1  = pg.TextItem("NO", anchor=(0.5, 0.5), color="r")
        parachute_status_text1.setFont(font)
        parachute_status_graph.addItem(parachute_status_text1)
    else:
        parachute_status_text1  = pg.TextItem("Yes", anchor=(0.5, 0.5), color="g")
        parachute_status_text1.setFont(font)
        parachute_status_graph.addItem(parachute_status_text1)

def update():
    try:
        value_chain = []
        value_chain = ser.getData()
        update_altitude(value_chain)
        update_vel(value_chain)
        update_acc(value_chain)
        update_gyro(value_chain)
        update_humidity(value_chain)
        update_pressure(value_chain)
        update_temp(value_chain)
        update_parachute(value_chain)
        update_camera(value_chain)
        update_transmitter(value_chain)
        update_MAP(value_chain)
        update_altitude(value_chain)

        data_base.guardar(value_chain)
    except IndexError:
        print('starting, please wait a moment')


if(ser.isOpen()) or (ser.dummyMode()):
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(500)
else:
    print("something is wrong with the update call")

# Start Qt event loop unless running in interactive mode.

if __name__ == '__main__':

    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
