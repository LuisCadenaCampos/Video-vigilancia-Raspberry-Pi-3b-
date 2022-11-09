"""
Autor original de deteccion de movimiento: Luis del Valle Hernández
Fecha de creacion de codigo original: 07 de Julio de 2016
Version: 1.0.0
Fuente: https://programarfacil.com/blog/vision-artificial/deteccion-de-movimiento-con-opencv-python/

Autor original de funcion def angle_to_percent:
Fecha de creacion de codigo original: 29 de Octubre del 2019
Version:1.0.0
Fuente:https://raspberrypi-espana.es/servo-frambuesa-pi/ 

Autor original de Mover un servo con Python y OpenCV: Abraham Gastélum 
Fecha de creacion del codigo: 1 abril del 2021
Version: 1.0.0
Fuente: https://www.automatizacionparatodos.com/vision-artificial-arduino/

Modificado por: Cadena Campos Luis
Fecha de modificacion: ...
Version de codigo modificado: 1.0.0
Correo:luis14oriente@gmail.com

""" 
#Definimos las bibliotecas a usar
#numpy, opencv, time, RPi.GPIO
import cv2
import numpy as np
import time
import RPi.GPIO as GPIO
from time import sleep

#Funcion para convertir de angulo a porcentaje
def angle_to_percent(angle) :
    if angle > 180 or angle <0:
        return False
    start = 4
    end   = 12.5
    ratio = (end - start)/180
    angle_as_percent=angle*ratio
    return start+angle_as_percent

#Declaracion de pins en modo board.
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False) 
GPIO.setup(32,GPIO.OUT)
servo=GPIO.PWM(32,50)
#Inicializamos el servo en 90°
servo.start(angle_to_percent(90))
#Iniciamos en la camara numero 1.
camara = cv2.VideoCapture(0)
#Ajustamos los FPS a 30
camara.set(cv2.CAP_PROP_FPS,30)
#Se intento grabar con open Cv
#video_grabado=cv2.VideoWriter('Grabacion.avi',cv2.VideoWriter_fourcc(*'DIVX'),30.0,(500,500))
#Desactivamos OpenCL
cv2.ocl.setUseOpenCL(False)
#Inicializamos a fondo,c iguales  NULL
fondo=None
c=None
#Inicializamos contornos en 0
contornos=0

while True:
	#Empezamos a capturar el video
	(grabbed,frame)=camara.read()
	if not grabbed:
		break
	#Transformamos la imagen de color a escala de grises
	gris=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
	#Aplicamos el filtro Gaussiano
	gris=cv2.GaussianBlur(gris,(21,21),0)
	if fondo is None:
		fondo=gris
		continue
	#Se calcula la diferencia entre el fondo y el frame actual
	resta=cv2.absdiff(fondo,gris)
	#Se aplica el umbral
	umbral=cv2.threshold(resta,180,255,cv2.THRESH_BINARY)[1] 
	#Dilatamos el umbral para tapar agujeros
	umbral=cv2.dilate(umbral,None,iterations=96)
	contornosimg=umbral.copy()
	#Detectamos los contornos
	contornos,hierarchy=cv2.findContours(contornosimg,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	#Buscamos en los contornos para
	#Obtener el centroide en X
	for c in contornos:
		if cv2.contourArea(c)<1200:
			#Obtenemos los momentos
			M=cv2.moments(c)
			if M["m00"] == 0:
				M["m00"]=1
			#Obtenemos el centroide en X
			x=int(M["m10"] / M["m00"])
			continue
	(x,y,w,h) = cv2.boundingRect(c)
	#Dibujamos un rectangulo sobre la persona
	cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
	#Establecemos una fuente
	font=cv2.FONT_HERSHEY_SIMPLEX
	#Mostramos la coordenada del centroide en X
	cv2.putText(frame,'x={}'.format(x,y),(x+10,y),font,1.0,(255,0,255),2,cv2.LINE_AA)
	#Movemos el servomotor dependiendo de la coordenada en X del centroide
	if 0<= x < 100:
		servo.ChangeDutyCycle(angle_to_percent(0))#0 Grados
	elif 200 > x >100:
		servo.ChangeDutyCycle(angle_to_percent(30))#30 Grados
	elif 300 > x >=200:
		servo.ChangeDutyCycle(angle_to_percent(60))#60 Grados
	elif 350 <= x < 400:
		servo.ChangeDutyCycle(angle_to_percent(90))#90 Grados
	elif 400 <= x <500: 
		servo.ChangeDutyCycle(angle_to_percent(120))#120 Grados
	elif 500 <= x <510:
		servo.ChangeDutyCycle(angle_to_percent(150))#150 Grados
	elif x >= 520 > 540:
		servo.ChangeDutyCycle(angle_to_percent(180))#180 Grados
	#Abrimos una ventana para mostrar la captura
	cv2.imshow("Camara",frame)
	#Se intento grabar el video obtenido
	#video_grabado("Camara",frame)
	key=cv2.waitKey(1) & 0xFF
	time.sleep(0.015)
	#Cerramos al presionar la tecla q
	if key==ord('q'):
		break		
camara.release()
#Detenemos la grabacion del video
#video_grabado.release()
cv2.destroyAllWindows()
GPIO.cleanup()
servo.stop()
#En las ultimas lineas cerramos las ventanas
#Y limpiamos los puertos gpio