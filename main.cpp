#include <esp32cam.h>
#include <WebServer.h>
#include <WiFi.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

const char* WIFI_SSID = "NETSULMINAS-Casa";
const char* WIFI_PASS = "Babebi123@";
unsigned int timer = millis() + 4000;

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

WebServer server(80);

const int flash = 4;
#define I2C_SDA 16
#define I2C_SCL 3
#define MIN_PULSE_WIDTH 650   //Estes são os valores mínimo e máximo de largura de pulso que servem para o MG 995.
#define MAX_PULSE_WIDTH 2350
#define DEFAULT_PULSE_WIDTH 1500
#define FREQUENCY 60
int servo = 0;

static auto hiRes = esp32cam::Resolution::find(800, 600);

int pulseWidth(int angle){ //Esta função calcula o ângulo de movimento do servo.

  int pulse_wide, analog_value;
  pulse_wide = map(angle, 0, 180, MIN_PULSE_WIDTH, MAX_PULSE_WIDTH); //Esta função pega ângulo de 0 a 180 graus e mapeia do valor mínimo de largura até o valor máximo. 
  analog_value = int(float(pulse_wide) / 1000000 * FREQUENCY * 4096);
  Serial.println(analog_value);
  return analog_value; //O valor que a função retorna.

}

void serveJpg()
{
  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("CAPTURE FAIL");
    server.send(503, "", "");
    return;
  }
  Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                static_cast<int>(frame->size()));

  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client);
}


void handleJpgHi()
{
  if (!esp32cam::Camera.changeResolution(hiRes)) {
    Serial.println("SET-HI-RES FAIL");
  }
  serveJpg();
}

void handleJpg()
{
  server.sendHeader("Location", "/cam-hi.jpg");
  server.send(302, "", "");
}


void setup()
{
  Serial.begin(115200);
  Serial.println();
  
  Wire.begin(I2C_SDA, I2C_SCL);
  pwm.begin();  //Inicializa a biblioteca e envia sinais PWM.
  pwm.setPWMFreq(FREQUENCY); //Frequência de atualização do servo a 60 Hertz.
  pwm.setPWM(0,0,pulseWidth(180)); 
  pwm.setPWM(1,0,pulseWidth(180)); 
  pwm.setPWM(2,0,pulseWidth(180)); 
  pwm.setPWM(3,0,pulseWidth(180)); 
  pwm.setPWM(4,0,pulseWidth(0));

  {
    using namespace esp32cam;
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(hiRes);
    cfg.setBufferCount(2);
    cfg.setJpeg(80);
    bool ok = Camera.begin(cfg);
    Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");
  }

  pinMode(flash, OUTPUT);

  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  Serial.print("http://");
  Serial.println(WiFi.localIP());
  Serial.println("  /cam-hi.jpg");
  server.on("/cam-hi.jpg", handleJpgHi);
  server.on("/flash", HTTP_GET, [](){
    server.send(200, "text/plain", "flash ligado!");
    digitalWrite(flash, HIGH);
  });
  server.on("/flash-desligado", HTTP_GET, [](){
    server.send(200, "text/plan", "flash desligado!");
    digitalWrite(flash, LOW);
  });

  server.on("/identificando-mao", HTTP_GET, [](){
    server.send(200,"text/plan", "tentando encontrar a mao");
    if(millis() > timer){
    digitalWrite(flash,HIGH);
    timer = millis() + 500;
    }
    else{
    digitalWrite(flash, LOW);
    }
  });
  
  server.on("/tesoura", HTTP_GET, [](){
    server.send(200,"text/plan", "Tesoura");
    pwm.setPWM(0, 0, pulseWidth(10));
    pwm.setPWM(1, 0, pulseWidth(10));
    pwm.setPWM(2, 0, pulseWidth(180));
    pwm.setPWM(3, 0, pulseWidth(180));
    pwm.setPWM(4, 0, pulseWidth(180));
  });

    server.on("/ativar", HTTP_GET, [](){
    server.send(200,"text/plan", "ativando");
    pwm.setPWM(0, 0, pulseWidth(10));
    delay(100);
    pwm.setPWM(1, 0, pulseWidth(10));
    delay(100);
    pwm.setPWM(2, 0, pulseWidth(10));
    delay(100);
    pwm.setPWM(3, 0, pulseWidth(10));
    delay(100);
    pwm.setPWM(4, 0, pulseWidth(180));
    delay(100);
    pwm.setPWM(0, 0, pulseWidth(180));
    delay(100);
    pwm.setPWM(1, 0, pulseWidth(180));
    delay(100);
    pwm.setPWM(2, 0, pulseWidth(180));
    delay(100);
    pwm.setPWM(3, 0, pulseWidth(180));
    delay(100);
    pwm.setPWM(4, 0, pulseWidth(0));
    delay(100);
  });

  server.on("/rock", HTTP_GET, [](){
    server.send(200,"text/plan", "rock");
    pwm.setPWM(0, 0, pulseWidth(180));
    pwm.setPWM(1, 0, pulseWidth(10));
    pwm.setPWM(2, 0, pulseWidth(10));
    pwm.setPWM(3, 0, pulseWidth(180));
    pwm.setPWM(4, 0, pulseWidth(0));
  });

  server.on("/papel", HTTP_GET, [](){
    server.send(200,"text/plan", "Papel");
    pwm.setPWM(0, 0, pulseWidth(180));
    pwm.setPWM(1, 0, pulseWidth(180));
    pwm.setPWM(2, 0, pulseWidth(180));
    pwm.setPWM(3, 0, pulseWidth(180));
    pwm.setPWM(4, 0, pulseWidth(0));
  });

  server.on("/pedra", HTTP_GET, [](){
    server.send(200,"text/plan", "Pedra");
    pwm.setPWM(0, 0, pulseWidth(10));
    pwm.setPWM(1, 0, pulseWidth(10));
    pwm.setPWM(2, 0, pulseWidth(10));
    pwm.setPWM(3, 0, pulseWidth(10));
    pwm.setPWM(4, 0, pulseWidth(180));
  });

  server.on("/meio", HTTP_GET, [](){
    server.send(200,"text/plan", "dedo do meio");
    pwm.setPWM(0, 0, pulseWidth(10));
    pwm.setPWM(1, 0, pulseWidth(10));
    pwm.setPWM(2, 0, pulseWidth(180));
    pwm.setPWM(3, 0, pulseWidth(10));
    pwm.setPWM(4, 0, pulseWidth(180));
  });

  server.begin();
}

void loop()
{
  server.handleClient();
}