#include <Servo.h>

Servo myservo_on;
Servo myservo_under;

const byte START_BYTE = 0x02;
const byte END_BYTE   = 0x03;

void setup() {
  Serial.begin(9600);

  myservo_under.attach(9); // Servo dưới
  myservo_on.attach(8);    // Servo trên

  myservo_under.write(90);   // Trung lập ban đầu
  myservo_on.write(90);
  delay(500);
}

void loop() {
  receive_data();
}

// ham xoay servo ve goc ban dau
void rotate_default () {
  myservo_under.write(90);  
  myservo_on.write(90);
}

void classify_bottle () {
  myservo_on.write(0); // nga mang xuong
  myservo_under.write(155); // quay sang trai
  delay(2000);
  rotate_default();
}

void classify_can () {
    myservo_on.write(0);  // nga mang xuong
    myservo_under.write(0);   // quay sang phai
    rotate_default();
}

// Nhận mảng 3 byte từ UART: [START, DATA, END]
void receive_data() {
  const int PACKET_SIZE = 3;
  byte buffer[PACKET_SIZE];

  while (Serial.available() >= PACKET_SIZE) {
    Serial.readBytes(buffer, PACKET_SIZE);

    if (buffer[0] == START_BYTE && buffer[2] == END_BYTE) {
      handle_command(buffer[1]);  // xử lý byte dữ liệu ở giữa
    } else {
      // Nếu không đúng định dạng, bỏ qua
      Serial.println("Gói không hợp lệ");
    }
  }
}

// Xử lý servo theo lệnh nhận
void handle_command(byte command) {
  Serial.print("Lệnh nhận: ");
  Serial.println(command, HEX);

  switch (command) {
    case 0x01:
    classify_bottle();
      break;

    case 0x02:
    classify_can();
      break;

    default:
      // Lệnh không hợp lệ
      Serial.println("Lệnh không hỗ trợ.");
      break;
  }
}
