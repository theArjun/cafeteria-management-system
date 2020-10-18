window.onload = () => {
    const particular = document.getElementById('id_particular');
    const add_particular_icon = document.getElementById('add_id_particular');
    let info= document.createElement('span')


    particular.addEventListener('change', () => {
        const itemValue = particular.value;
        const endpoint = `/api/v1/get_stock/${itemValue}`
        fetch(endpoint)
            .then(res => res.json())
            .then(data => {
                const stock = data.stock;
                info.innerHTML = `Stock Remaining : ${stock}`;
                add_particular_icon.innerHTML = '';
                add_particular_icon.insertAdjacentElement('afterend', info);
            })
            .catch(error => {
                console.log(error)
            })
    })
}