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