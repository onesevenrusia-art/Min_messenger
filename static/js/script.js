fetch("/", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({}),
    })
    .then(response => response.json())
    .then(result => {

    })
    .catch(error => {
        console.error("Ошибка сети:", error);
    });