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
    const keyPair = await crypto.subtle.generateKey(
        {
            name: "RSA-OAEP",
            modulusLength: 2048,
            publicExponent: new Uint8Array([1, 0, 1]),
            hash: "SHA-256",
        },
        true,
        ["encrypt", "decrypt"]
    );

    const exportedPublicKey = await crypto.subtle.exportKey("spki", keyPair.publicKey);
    const exportedPrivateKey = await crypto.subtle.exportKey("pkcs8", keyPair.privateKey);

    return {
        publicKey: arrayBufferToBase64(exportedPublicKey),
        privateKey: arrayBufferToBase64(exportedPrivateKey)
    };
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

// 3. Импорт ключей
async function importPublicKey(publicKeyB64) {
    const keyData = base64ToArrayBuffer(publicKeyB64);
    return await crypto.subtle.importKey(
        "spki",
        keyData,
        { name: "RSA-OAEP", hash: "SHA-256" },
        true,
        ["encrypt"]
    );
}

async function importPrivateKey(privateKeyB64) {
    const keyData = base64ToArrayBuffer(privateKeyB64);
    return await crypto.subtle.importKey(
        "pkcs8",
        keyData,
        { name: "RSA-OAEP", hash: "SHA-256" },
        true,
        ["decrypt"]
    );
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

async function encryptMessage(message, recipientPublicKeyB64) {
    try {
        console.log('🔐 encryptMessage вызвана с параметрами:');
        console.log('message:', typeof message, 'длина:', message?.length);
        console.log('recipientPublicKeyB64:', typeof recipientPublicKeyB64);
        console.log('recipientPublicKeyB64 первые 100 символов:', recipientPublicKeyB64?.substring(0, 100));
        console.log('recipientPublicKeyB64 длина:', recipientPublicKeyB64?.length);
        
        // 🔍 КРИТИЧЕСКАЯ ПРОВЕРКА
        if (!recipientPublicKeyB64 || typeof recipientPublicKeyB64 !== 'string') {
            console.error('❌ recipientPublicKeyB64 не строка:', recipientPublicKeyB64);
            throw new Error('Публичный ключ должен быть строкой');
        }
        
        // Проверяем что это действительно base64 (начинается с MIIBI)
        if (!recipientPublicKeyB64.startsWith('MIIBI')) {
            console.error('❌ Ключ не начинается с MIIBI!');
            console.error('Начинается с:', recipientPublicKeyB64.substring(0, 20));
            console.error('Возможно, это JSON объект?');
            
            // Может быть это JSON строка?
            try {
                const parsed = JSON.parse(recipientPublicKeyB64);
                console.error('Это JSON объект!', parsed);
                console.error('Используйте parsed.publickey или parsed.publickeycrypt');
            } catch (e) {
                console.error('Не JSON, просто неправильная строка');
            }
            
            throw new Error('Неверный формат публичного ключа');
        }
        
        // Дальше ваш код...
        const publicKey = await importPublicKey(publicKeyB64);
        const encoder = new TextEncoder();
        const data = encoder.encode(message);
        
        const encryptedData = await crypto.subtle.encrypt(
            { name: "RSA-OAEP" },
            publicKey,
            data
        );
        
        return arrayBufferToBase64(encryptedData);
        // ...
        
    } catch (error) {
        console.error('❌ Ошибка в encryptMessage:', error);
        throw error;
    }
}



// 5. Расшифровка
async function decryptMessage(encryptedMessageB64, privateKeyB64) {
    const privateKey = await importPrivateKey(privateKeyB64);
    const encryptedData = base64ToArrayBuffer(encryptedMessageB64);
    
    const decryptedData = await crypto.subtle.decrypt(
        { name: "RSA-OAEP" },
        privateKey,
        encryptedData
    );
    
    const decoder = new TextDecoder();
    return decoder.decode(decryptedData);
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