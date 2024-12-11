var currentId = 0;
        var amount_authors = 0;

        function show_upload_dataset() {
            document.getElementById("upload_dataset").style.display = "block";
        }

        function generateIncrementalId() {
            return currentId++;
        }

        function addField(newAuthor, name, text, className = 'col-lg-6 col-12 mb-3') {
            let fieldWrapper = document.createElement('div');
            fieldWrapper.className = className;

            let label = document.createElement('label');
            label.className = 'form-label';
            label.for = name;
            label.textContent = text;

            let field = document.createElement('input');
            field.name = name;
            field.className = 'form-control';

            fieldWrapper.appendChild(label);
            fieldWrapper.appendChild(field);
            newAuthor.appendChild(fieldWrapper);
        }

        function addRemoveButton(newAuthor) {
            let buttonWrapper = document.createElement('div');
            buttonWrapper.className = 'col-12 mb-2';

            let button = document.createElement('button');
            button.textContent = 'Remove author';
            button.className = 'btn btn-danger btn-sm';
            button.type = 'button';
            button.addEventListener('click', function (event) {
                event.preventDefault();
                newAuthor.remove();
            });

            buttonWrapper.appendChild(button);
            newAuthor.appendChild(buttonWrapper);
        }

        function createAuthorBlock(idx, suffix) {
            let newAuthor = document.createElement('div');
            newAuthor.className = 'author row';
            newAuthor.style.cssText = "border:2px dotted #ccc;border-radius:10px;padding:10px;margin:10px 0; background-color: white";

            addField(newAuthor, `${suffix}authors-${idx}-name`, 'Name *');
            addField(newAuthor, `${suffix}authors-${idx}-affiliation`, 'Affiliation');
            addField(newAuthor, `${suffix}authors-${idx}-orcid`, 'ORCID');
            addRemoveButton(newAuthor);

            return newAuthor;
        }

        function check_title_and_description() {
            let titleInput = document.querySelector('input[name="title"]');
            let descriptionTextarea = document.querySelector('textarea[name="desc"]');

            titleInput.classList.remove("error");
            descriptionTextarea.classList.remove("error");
            clean_upload_errors();

            let titleLength = titleInput.value.trim().length;
            let descriptionLength = descriptionTextarea.value.trim().length;

            if (titleLength < 3) {
                write_upload_error("title must be of minimum length 3");
                titleInput.classList.add("error");
            }

            if (descriptionLength < 3) {
                write_upload_error("description must be of minimum length 3");
                descriptionTextarea.classList.add("error");
            }

            return (titleLength >= 3 && descriptionLength >= 3);
        }


        document.getElementById('add_author').addEventListener('click', function () {
            let authors = document.getElementById('authors');
            let newAuthor = createAuthorBlock(amount_authors++, "");
            authors.appendChild(newAuthor);
        });


        document.addEventListener('click', function (event) {
            if (event.target && event.target.classList.contains('add_author_to_uvl')) {

                let authorsButtonId = event.target.id;
                let authorsId = authorsButtonId.replace("_button", "");
                let authors = document.getElementById(authorsId);
                let id = authorsId.replace("_form_authors", "")
                let newAuthor = createAuthorBlock(amount_authors, `feature_models-${id}-`);
                authors.appendChild(newAuthor);

            }
        });

        function show_loading() {
            document.getElementById("upload_button").style.display = "none";
            document.getElementById("loading").style.display = "block";
        }

        function hide_loading() {
            document.getElementById("upload_button").style.display = "block";
            document.getElementById("loading").style.display = "none";
        }

        function clean_upload_errors() {
            let upload_error = document.getElementById("upload_error");
            upload_error.innerHTML = "";
            upload_error.style.display = 'none';
        }

        function write_upload_error(error_message) {
            let upload_error = document.getElementById("upload_error");
            let alert = document.createElement('p');
            alert.style.margin = '0';
            alert.style.padding = '0';
            alert.textContent = 'Upload error: ' + error_message;
            upload_error.appendChild(alert);
            upload_error.style.display = 'block';
        }

        window.onload = function () {

            test_zenodo_connection();
            if (window.location.pathname.startsWith('/dataset/upload')) {
                document.getElementById('create_button').addEventListener('click', function () {
                    // process data form
                    const formData = {};
    
                    ["basic_info_form", "uploaded_models_form"].forEach((formId) => {
                        const form = document.getElementById(formId);
                        const inputs = form.querySelectorAll('input, select, textarea');
                        inputs.forEach(input => {
                            if (input.name) {
                                formData[input.name] = formData[input.name] || [];
                                formData[input.name].push(input.value);
                            }
                        });
                    });
    
                    let formDataJson = JSON.stringify(formData);
                    console.log(formDataJson);
    
                    const csrfToken = document.getElementById('csrf_token').value;
                    const formUploadData = new FormData();
                    formUploadData.append('csrf_token', csrfToken);
    
                    for (let key in formData) {
                        if (formData.hasOwnProperty(key)) {
                            formUploadData.set(key, formData[key]);
                        }
                    }
    
                    let checked_orcid = true;
                    if (Array.isArray(formData.author_orcid)) {
                        for (let orcid of formData.author_orcid) {
                            orcid = orcid.trim();
                            if (orcid !== '' && !isValidOrcid(orcid)) {
                                hide_loading();
                                write_upload_error("ORCID value does not conform to valid format: " + orcid);
                                checked_orcid = false;
                                break;
                            }
                        }
                    }
    
    
                    let checked_name = true;
                    if (Array.isArray(formData.author_name)) {
                        for (let name of formData.author_name) {
                            name = name.trim();
                            if (name === '') {
                                hide_loading();
                                write_upload_error("The author's name cannot be empty");
                                checked_name = false;
                                break;
                            }
                        }
                    }
    
    
                    if (checked_orcid && checked_name) {
                        fetch('/dataset/create', {
                            method: 'POST',
                            body: formUploadData
                        })
                            .then(response => {
                                if (response.ok) {
                                    console.log('Dataset enviado con éxito');
                                    response.json().then(data => {
                                        console.log(data.message);
                                        window.location.href = "/dataset/list";
                                    });
                                } else {
                                    // Extraer el mensaje de error desde el objeto JSON
                                    response.json().then(data => {
                                        console.error('Error en la solicitud:', data);
                                        console.log("Mensaje de error: ", data.message || JSON.stringify(data));
                                        hide_loading();
                        
                                        // Asegúrate de que `data.message` exista, o muestra todo el objeto si no
                                        write_upload_error(data.message || "Error desconocido en el servidor");
                                    });
                                }
                            })
                            .catch(error => {
                                console.error('Error en la solicitud POST:', error);
                            });
                    }
    
                        
                    function write_upload_error(error) {
                        const errorMessage = typeof error === "string" ? error : JSON.stringify(error);
                        // Muestra el mensaje de error en el DOM
                        document.getElementById("error_message").innerText = errorMessage;
                    }
    
                });
            }
            

            document.getElementById('upload_button').addEventListener('click', function () {
                let url;
                if (window.location.pathname.startsWith('/dataset/staging-area')) {
                    const datasetId = window.location.pathname.split('/').pop(); // Extract the dataset ID from the URL
                    url = `/dataset/upload/${datasetId}`; // Use the new route for staging area updates
                } else {
                    url = '/dataset/upload'; // Default to the upload route
                }
                clean_upload_errors();
                show_loading();

                // check title and description
                let check = check_title_and_description();

                if (check) {
                    // process data form
                    const formData = {};

                    ["basic_info_form", "uploaded_models_form"].forEach((formId) => {
                        const form = document.getElementById(formId);
                        const inputs = form.querySelectorAll('input, select, textarea');
                        inputs.forEach(input => {
                            if (input.name) {
                                formData[input.name] = formData[input.name] || [];
                                formData[input.name].push(input.value);
                            }
                        });
                    });

                    let formDataJson = JSON.stringify(formData);
                    console.log(formDataJson);

                    const csrfToken = document.getElementById('csrf_token').value;
                    const formUploadData = new FormData();
                    formUploadData.append('csrf_token', csrfToken);

                    for (let key in formData) {
                        if (formData.hasOwnProperty(key)) {
                            formUploadData.set(key, formData[key]);
                        }
                    }

                    let checked_orcid = true;
                    if (Array.isArray(formData.author_orcid)) {
                        for (let orcid of formData.author_orcid) {
                            orcid = orcid.trim();
                            if (orcid !== '' && !isValidOrcid(orcid)) {
                                hide_loading();
                                write_upload_error("ORCID value does not conform to valid format: " + orcid);
                                checked_orcid = false;
                                break;
                            }
                        }
                    }


                    let checked_name = true;
                    if (Array.isArray(formData.author_name)) {
                        for (let name of formData.author_name) {
                            name = name.trim();
                            if (name === '') {
                                hide_loading();
                                write_upload_error("The author's name cannot be empty");
                                checked_name = false;
                                break;
                            }
                        }
                    }


                    if (checked_orcid && checked_name) {
                        fetch(url, {
                            method: 'POST',
                            body: formUploadData
                        })
                            .then(response => {
                                if (response.ok) {
                                    console.log('Dataset sent successfully');
                                    response.json().then(data => {
                                        console.log(data.message);
                                        window.location.href = "/dataset/list";
                                    });
                                } else {
                                    response.json().then(data => {
                                        console.error('Error: ' + data.message);
                                        hide_loading();

                                        write_upload_error(data.message);

                                    });
                                }
                            })
                            .catch(error => {
                                console.error('Error in POST request:', error);
                            });
                    }


                } else {
                    hide_loading();
                }


            });
            document.getElementById('upload_fakenodo_button').addEventListener('click', function () {
                let url;
                if (window.location.pathname.startsWith('/dataset/staging-area')) {
                    const datasetId = window.location.pathname.split('/').pop(); // Extract the dataset ID from the URL
                    url = `/dataset/upload-fakenodo/${datasetId}`; // Use the new route for staging area updates
                } else {
                    url = '/dataset/upload-fakenodo'; // Default to the upload route
                }
                clean_upload_errors();
                show_loading();

                // check title and description
                let check = check_title_and_description();

                if (check) {
                    // process data form
                    const formData = {};

                    ["basic_info_form", "uploaded_models_form"].forEach((formId) => {
                        const form = document.getElementById(formId);
                        const inputs = form.querySelectorAll('input, select, textarea');
                        inputs.forEach(input => {
                            if (input.name) {
                                formData[input.name] = formData[input.name] || [];
                                formData[input.name].push(input.value);
                            }
                        });
                    });

                    let formDataJson = JSON.stringify(formData);
                    console.log(formDataJson);

                    const csrfToken = document.getElementById('csrf_token').value;
                    const formUploadData = new FormData();
                    formUploadData.append('csrf_token', csrfToken);

                    for (let key in formData) {
                        if (formData.hasOwnProperty(key)) {
                            formUploadData.set(key, formData[key]);
                        }
                    }

                    let checked_orcid = true;
                    if (Array.isArray(formData.author_orcid)) {
                        for (let orcid of formData.author_orcid) {
                            orcid = orcid.trim();
                            if (orcid !== '' && !isValidOrcid(orcid)) {
                                hide_loading();
                                write_upload_error("ORCID value does not conform to valid format: " + orcid);
                                checked_orcid = false;
                                break;
                            }
                        }
                    }


                    let checked_name = true;
                    if (Array.isArray(formData.author_name)) {
                        for (let name of formData.author_name) {
                            name = name.trim();
                            if (name === '') {
                                hide_loading();
                                write_upload_error("The author's name cannot be empty");
                                checked_name = false;
                                break;
                            }
                        }
                    }


                    if (checked_orcid && checked_name) {
                        fetch(url, {
                            method: 'POST',
                            body: formUploadData
                        })
                            .then(response => {
                                if (response.ok) {
                                    console.log('Dataset sent successfully');
                                    response.json().then(data => {
                                        console.log(data.message);
                                        window.location.href = "/dataset/list";
                                    });
                                } else {
                                    response.json().then(data => {
                                        console.error('Error: ' + data.message);
                                        hide_loading();

                                        write_upload_error(data.message);

                                    });
                                }
                            })
                            .catch(error => {
                                console.error('Error in POST request:', error);
                            });
                    }


                } else {
                    hide_loading();
                }


            });
        };
        if (window.location.pathname.startsWith('/dataset/staging-area')) {
            document.getElementById('update_button').addEventListener('click', function () {
                // process data form
                clean_upload_errors();
                show_loading();
                const formData = {};

                ["basic_info_form", "uploaded_models_form"].forEach((formId) => {
                    const form = document.getElementById(formId);
                    const inputs = form.querySelectorAll('input, select, textarea');
                    inputs.forEach(input => {
                        if (input.name) {
                            formData[input.name] = formData[input.name] || [];
                            formData[input.name].push(input.value);
                        }
                    });
                });

                let formDataJson = JSON.stringify(formData);
                console.log(formDataJson);

                const csrfToken = document.getElementById('csrf_token').value;
                const formUploadData = new FormData();
                formUploadData.append('csrf_token', csrfToken);

                for (let key in formData) {
                    if (formData.hasOwnProperty(key)) {
                        formUploadData.set(key, formData[key]);
                    }
                }

                let checked_orcid = true;
                if (Array.isArray(formData.author_orcid)) {
                    for (let orcid of formData.author_orcid) {
                        orcid = orcid.trim();
                        if (orcid !== '' && !isValidOrcid(orcid)) {
                            hide_loading();
                            write_upload_error("ORCID value does not conform to valid format: " + orcid);
                            checked_orcid = false;
                            break;
                        }
                    }
                }


                let checked_name = true;
                if (Array.isArray(formData.author_name)) {
                    for (let name of formData.author_name) {
                        name = name.trim();
                        if (name === '') {
                            hide_loading();
                            write_upload_error("The author's name cannot be empty");
                            checked_name = false;
                            break;
                        }
                    }
                }


                if (checked_orcid && checked_name) {
                    fetch(window.location.pathname, {
                        method: 'POST',
                        body: formUploadData
                    })
                        .then(response => {
                            console.log(formUploadData);
                            if (response.ok) {
                                console.log('Dataset enviado con éxito');
                                window.location.href = "/dataset/list";
                                response.json().then(() => {
                                    window.location.href = "/dataset/list";
                                        });
                            } else {
                                // Extraer el mensaje de error desde el objeto JSON
                                response.json().then(data => {
                                    console.error('Error en la solicitud:', data);
                                    console.log("Mensaje de error: ", data.message || JSON.stringify(data));
                                    hide_loading();
                    
                                    // Asegúrate de que `data.message` exista, o muestra todo el objeto si no
                                    write_upload_error(data.message || "Error desconocido en el servidor");
                                });
                            }
                        })
                        .catch(error => {
                            console.log(formUploadData);
                            console.error('Error en la solicitud POST:', error);
                        });
                }

                    
                function write_upload_error(error) {
                    const errorMessage = typeof error === "string" ? error : JSON.stringify(error);
                    // Muestra el mensaje de error en el DOM
                    document.getElementById("error_message").innerText = errorMessage;
                }

            });
        }


        function isValidOrcid(orcid) {
            let orcidRegex = /^\d{4}-\d{4}-\d{4}-\d{4}$/;
            return orcidRegex.test(orcid);
        }