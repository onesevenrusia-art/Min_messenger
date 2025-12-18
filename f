тут некоторыефункции которыенеобходимы в приложении - подпись челенжа , гибридная расшифровка генерация ключей для подписи и шифрования          
          
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
