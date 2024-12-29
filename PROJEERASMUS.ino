int relayPin = 7;        // Röle D7 pinine bağlı
int soilSensorPin = A5;  // Nem sensörü A5 pinine bağlı
int soilValue = 0;       // Nem sensör değeri
int targetMoisture = 700; // Varsayılan hedef nem seviyesi
bool aiMode = false;     // Yapay zeka modu aktif/pasif kontrolü

void setup() {
  Serial.begin(9600);
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, HIGH); // Röle başlangıçta kapalı
}

void loop() {
  // Nem sensöründen değer oku
  soilValue = analogRead(soilSensorPin);

  // Seri port üzerinden Python'a nem değerini gönder
  Serial.println(soilValue);
  delay(1000); // 1 saniyelik gecikme ile okuma

  // Yapay zeka modu aktifse ve nem seviyesi hedefin altındaysa sulama yap
  if (aiMode && soilValue < targetMoisture) {
    digitalWrite(relayPin, LOW); // Röleyi aç (sulama başlasın)
  } else if (aiMode && soilValue >= targetMoisture) {
    digitalWrite(relayPin, HIGH); // Röleyi kapat (sulama durur)
  }

  // Python'dan gelen komutu işle
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Tam komutu oku

    if (command.startsWith("S")) { // 'S' komutu sulamayı manuel başlatır
      digitalWrite(relayPin, LOW);
      aiMode = false; // Manuel modda AI devre dışı
    } 
    else if (command.startsWith("T")) { // 'T' komutu sulamayı manuel durdurur
      digitalWrite(relayPin, HIGH);
      aiMode = false; // Manuel modda AI devre dışı
    }
    else if (command.startsWith("A")) { // 'A' komutu yapay zeka modunu etkinleştirir
      aiMode = true;
    }
    else if (command.startsWith("D")) { // 'D' komutu yapay zeka modunu devre dışı bırakır
      aiMode = false;
      digitalWrite(relayPin, HIGH); // AI kapatılınca röleyi kapat
    }
    else if (command.startsWith("M")) { // 'M' ile başlayan komut nem eşiğini ayarlar
      int newMoisture = command.substring(1).toInt(); // 'M' sonrası gelen değeri al
      targetMoisture = newMoisture;
    }
  }
}
