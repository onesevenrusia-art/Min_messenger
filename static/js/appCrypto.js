        // 1. Вспомогательные функции
        function arrayBufferToBase64(buffer) {
            const bytes = new Uint8Array(buffer);
            let binary = '';
            for (let i = 0; i < bytes.byteLength; i++) {
                binary += String.fromCharCode(bytes[i]);
            }
            return btoa(binary);
        }

        function base64ToArrayBuffer(base64) {
            const binaryString = atob(base64);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            return bytes.buffer;
        }

        // 2. Генерация ключей шифрования
        async function generateEncryptionKeyPair() {
            const keyPair = await crypto.subtle.generateKey({
                    name: "RSA-OAEP",
                    modulusLength: 2048,
                    publicExponent: new Uint8Array([1, 0, 1]),
                    hash: "SHA-256",
                },
                true, ["encrypt", "decrypt"]
            );

            const exportedPublicKey = await crypto.subtle.exportKey("spki", keyPair.publicKey);
            const exportedPrivateKey = await crypto.subtle.exportKey("pkcs8", keyPair.privateKey);

            return {
                publicKey: arrayBufferToBase64(exportedPublicKey),
                privateKey: arrayBufferToBase64(exportedPrivateKey)
            };
        }

        // 3. Импорт ключей
        async function importPublicKey(publicKeyB64) {
            const keyData = base64ToArrayBuffer(publicKeyB64);
            return await crypto.subtle.importKey(
                "spki",
                keyData, {
                    name: "RSA-OAEP",
                    hash: "SHA-256"
                },
                true, ["encrypt"]
            );
        }

        async function importPrivateKey(privateKeyB64) {
            const keyData = base64ToArrayBuffer(privateKeyB64);
            return await crypto.subtle.importKey(
                "pkcs8",
                keyData, {
                    name: "RSA-OAEP",
                    hash: "SHA-256"
                },
                true, ["decrypt"]
            );
        }

        // 4. Шифрование
        async function encryptMessage(message, publicKeyB64) {
            const publicKey = await importPublicKey(publicKeyB64);
            const encoder = new TextEncoder();
            const data = encoder.encode(message);

            const encryptedData = await crypto.subtle.encrypt({
                    name: "RSA-OAEP"
                },
                publicKey,
                data
            );

            return arrayBufferToBase64(encryptedData);
        }

        // 5. Расшифровка
        async function decryptMessage(encryptedMessageB64, privateKeyB64) {
            const privateKey = await importPrivateKey(privateKeyB64);
            const encryptedData = base64ToArrayBuffer(encryptedMessageB64);

            const decryptedData = await crypto.subtle.decrypt({
                    name: "RSA-OAEP"
                },
                privateKey,
                encryptedData
            );

            const decoder = new TextDecoder();
            return decoder.decode(decryptedData);
        }



        // ===========================================
        // НОВЫЕ ФУНКЦИИ ДЛЯ ГИБРИДНОГО ШИФРОВАНИЯ
        // ===========================================

        // 4. ГИБРИДНОЕ ШИФРОВАНИЕ (для больших данных)
        async function hybridEncrypt(message, publicKeyB64) {
            // 1. Генерируем случайный AES ключ для этого сообщения
            const aesKey = await crypto.subtle.generateKey({
                    name: "AES-GCM",
                    length: 256
                },
                true, // extractable
                ["encrypt", "decrypt"]
            );

            // 2. Генерируем случайный IV (Initialization Vector)
            const iv = crypto.getRandomValues(new Uint8Array(12)); // 12 байт для GCM

            // 3. Шифруем сообщение AES-GCM
            const encoder = new TextEncoder();
            const data = encoder.encode(message);

            const encryptedData = await crypto.subtle.encrypt({
                    name: "AES-GCM",
                    iv: iv
                },
                aesKey,
                data
            );

            // 4. Экспортируем AES ключ и шифруем его RSA
            const exportedAesKey = await crypto.subtle.exportKey("raw", aesKey);
            const publicKey = await importPublicKey(publicKeyB64);
            const encryptedAesKey = await crypto.subtle.encrypt({
                    name: "RSA-OAEP"
                },
                publicKey,
                exportedAesKey
            );

            // 5. Возвращаем всё вместе
            return {
                encryptedKey: arrayBufferToBase64(encryptedAesKey), // Зашифрованный AES ключ
                encryptedData: arrayBufferToBase64(encryptedData), // Зашифрованные данные
                iv: arrayBufferToBase64(iv), // IV для AES-GCM
                algorithm: "AES-GCM-256+RSA-OAEP-2048" // Метка алгоритма
            };
        }

        // 5. ГИБРИДНАЯ РАСШИФРОВКА
        async function hybridDecrypt(encryptedPackage, privateKeyB64) {
            // 1. Расшифровываем AES ключ с помощью RSA
            const privateKey = await importPrivateKey(privateKeyB64);
            const encryptedKeyBuffer = base64ToArrayBuffer(encryptedPackage.encryptedKey);

            const aesKeyBytes = await crypto.subtle.decrypt({
                    name: "RSA-OAEP"
                },
                privateKey,
                encryptedKeyBuffer
            );

            // 2. Импортируем AES ключ
            const aesKey = await crypto.subtle.importKey(
                "raw",
                aesKeyBytes, {
                    name: "AES-GCM"
                },
                false, // not extractable
                ["decrypt"]
            );

            // 3. Расшифровываем данные AES-GCM
            const iv = base64ToArrayBuffer(encryptedPackage.iv);
            const encryptedData = base64ToArrayBuffer(encryptedPackage.encryptedData);

            const decryptedData = await crypto.subtle.decrypt({
                    name: "AES-GCM",
                    iv: new Uint8Array(iv)
                },
                aesKey,
                encryptedData
            );

            // 4. Декодируем текст
            const decoder = new TextDecoder();
            return decoder.decode(decryptedData);
        }


        async function generateKeyPair() {
            try {
                // Генерируем ключевую пару
                const keyPair = await crypto.subtle.generateKey({
                        name: "RSA-OAEP",
                        modulusLength: 2048,
                        publicExponent: new Uint8Array([1, 0, 1]),
                        hash: "SHA-256",
                    },
                    true, // extractable - можно экспортировать
                    ["encrypt", "decrypt"]
                );

                // Экспортируем ключи в формате base64
                const exportedPublic = await crypto.subtle.exportKey(
                    "spki",
                    keyPair.publicKey // ✅ Правильно передаем CryptoKey объект
                );
                const exportedPrivate = await crypto.subtle.exportKey(
                    "pkcs8",
                    keyPair.privateKey // ✅ Правильно передаем CryptoKey объект
                );

                // Конвертируем ArrayBuffer в base64
                const publicKeyB64 = arrayBufferToBase64(exportedPublic);
                const privateKeyB64 = arrayBufferToBase64(exportedPrivate);

                return {
                    publickey: publicKeyB64,
                    privateKey: privateKeyB64
                };

            } catch (error) {
                console.error('❌ Ошибка генерации ключей:', error);
                throw error;
            }
        }

        // 🔧 ОСТАВЬ эти функции без изменений:
        async function importPrivateKeyChallengs(privateKeyB64) {
            try {
                //console.log('🔑 Импортирую ключ...');
                const binaryString = atob(privateKeyB64);
                const bytes = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) {
                    bytes[i] = binaryString.charCodeAt(i);
                }
                const privateKey = await crypto.subtle.importKey(
                    "pkcs8",
                    bytes, {
                        name: "RSA-PSS",
                        hash: {
                            name: "SHA-256"
                        }
                    },
                    true, ["sign"]
                );
                //console.log('✅ Приватный ключ импортирован');
                return privateKey;
            } catch (error) {
                console.error('❌ Ошибка импорта ключа:', error);
                throw error;
            }
        }

        async function blobToArrayBuffer(blobOrFile) {
            if (blobOrFile instanceof Blob) {
                return await blobOrFile.arrayBuffer();
            }

            // Если DataURL
            if (typeof blobOrFile === "string" && blobOrFile.startsWith("data:")) {
                const res = await fetch(blobOrFile);
                return await res.arrayBuffer();
            }

            throw new Error("toArrayBuffer: не Blob и не DataURL");
        }

        async function encryptBlob(blob, publicKeyB64) {
            if (!(blob instanceof Blob)) {
                throw new Error("encryptBlob: input is not Blob");
            }

            // 1. Blob → ArrayBuffer
            const dataBuffer = await blob.arrayBuffer();

            // 2. AES-256-GCM key
            const aesKey = await crypto.subtle.generateKey({ name: "AES-GCM", length: 256 },
                true, ["encrypt"]
            );

            // 3. IV
            const iv = crypto.getRandomValues(new Uint8Array(12));

            // 4. Encrypt data (ANY BYTES)
            const encryptedData = await crypto.subtle.encrypt({ name: "AES-GCM", iv },
                aesKey,
                dataBuffer
            );

            // 5. Encrypt AES key with RSA
            const rawAesKey = await crypto.subtle.exportKey("raw", aesKey);
            const publicKey = await importPublicKey(publicKeyB64);

            const encryptedKey = await crypto.subtle.encrypt({ name: "RSA-OAEP" },
                publicKey,
                rawAesKey
            );

            // 6. Result package
            return {
                encryptedKey: arrayBufferToBase64(encryptedKey),
                encryptedData: arrayBufferToBase64(encryptedData),
                iv: arrayBufferToBase64(iv),
                mime: blob.type,
                size: blob.size
            };
        }

        async function decryptBlob(encryptedPackage, privateKeyB64) {

            // 1. RSA → AES key
            const encryptedKeyBuffer = base64ToArrayBuffer(
                encryptedPackage.encryptedKey
            );

            const privateKey = await importPrivateKey(privateKeyB64);

            const rawAesKey = await crypto.subtle.decrypt({ name: "RSA-OAEP" },
                privateKey,
                encryptedKeyBuffer
            );

            // 2. Import AES key
            const aesKey = await crypto.subtle.importKey(
                "raw",
                rawAesKey, { name: "AES-GCM" },
                false, ["decrypt"]
            );

            // 3. Decrypt data
            const encryptedData = base64ToArrayBuffer(
                encryptedPackage.encryptedData
            );

            const iv = base64ToArrayBuffer(encryptedPackage.iv);

            const decryptedBuffer = await crypto.subtle.decrypt({ name: "AES-GCM", iv: new Uint8Array(iv) },
                aesKey,
                encryptedData
            );

            // 4. ArrayBuffer → Blob
            return new Blob(
                [decryptedBuffer], { type: encryptedPackage.mime }
            );
        }

        function cleanPrivateKey(privateKeyData) {
            if (privateKeyData.includes('-----BEGIN')) {
                return privateKeyData
                    .replace(/-----BEGIN PRIVATE KEY-----/g, '')
                    .replace(/-----END PRIVATE KEY-----/g, '')
                    .replace(/-----BEGIN RSA PRIVATE KEY-----/g, '')
                    .replace(/-----END RSA PRIVATE KEY-----/g, '')
                    .replace(/\s/g, ''); // Убираем ВСЕ пробелы и переносы
            }
            return privateKeyData.replace(/\s/g, '');
        }

        // 🔧 НОВАЯ ФУНКЦИЯ - подпись challenge
        async function signChallenge(challenge, privateKeyData) {
            try {
                const privateKeyB64 = cleanPrivateKey(privateKeyData);
                const privateKey = await importPrivateKeyChallengs(privateKeyB64);
                const signature = await crypto.subtle.sign({
                        name: "RSA-PSS",
                        saltLength: 32
                    },
                    privateKey,
                    new TextEncoder().encode(challenge)
                );
                const signatureB64 = arrayBufferToBase64(signature);
                return signatureB64;

            } catch (error) {
                console.error('❌ Ошибка в signChallenge:', error);
                throw error;
            }
        }

        async function encryptMetadata(fileKey, metadata) {

            const iv = crypto.getRandomValues(
                new Uint8Array(12)
            );
        
            const encoded = new TextEncoder().encode(
                JSON.stringify(metadata)
            );
        
            const cipher = await crypto.subtle.encrypt(
                {
                    name: "AES-GCM",
                    iv: iv
                },
                fileKey,
                encoded
            );
        
            return {
                cipher,
                iv
            };
        }
        
        async function encryptChunk(fileKey, buffer) {
        
            const iv = crypto.getRandomValues(
                new Uint8Array(12)
            );
        
            const cipher = await crypto.subtle.encrypt(
                {
                    name: "AES-GCM",
                    iv: iv
                },
                fileKey,
                buffer
            );
        
            return {
                cipher,
                iv
            };
        }
        
        async function encryptFileKey(fileKey, publicKeyB64) {
        
            const rawKey = await crypto.subtle.exportKey(
                "raw",
                fileKey
            );
        
            const publicKey = await importPublicKey(
                publicKeyB64
            );
        
            const encrypted = await crypto.subtle.encrypt(
                {
                    name: "RSA-OAEP"
                },
                publicKey,
                rawKey
            );
        
            return encrypted;
        }
        

        window.generateEncryptionKeyPair = generateEncryptionKeyPair;
        window.generateKeyPair = generateEncryptionKeyPair;
        window.arrayBufferToBase64 = arrayBufferToBase64;
        window.base64ToArrayBuffer = base64ToArrayBuffer;
        window.encryptMessage = encryptMessage;
        window.decryptMessage = decryptMessage;
        window.signChallenge = signChallenge;
        window.cleanPrivateKey = cleanPrivateKey;
        window.importPrivateKey = importPrivateKey;
        window.importPrivateKeyChallengs = importPrivateKeyChallengs;
        window.importPublicKey = importPublicKey;
        window.hybridEncrypt = hybridEncrypt;
        window.hybridDecrypt = hybridDecrypt;
        window.encryptBlob = encryptBlob;
        window.decryptBlob = decryptBlob;
        window.encryptMetadata = encryptMetadata;
        window.encryptFileKey = encryptFileKey;
        window.encryptChunk = encryptChunk;
