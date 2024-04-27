<script setup>
    import { ref, onMounted } from "vue";
    import router from "../router/index";

    let csrf_token = ref("");
    let current_user_id = ref("");
    let jwt_token = ref("");

    let info = ref(false);


let getCsrfToken = async () => {
    const response = await fetch('/api/v1/csrf-token');
    return response.json();
};


let getUserId = async () => {
    const response = await fetch('/api/v1/loggedin');
    return response.json();
};


let getJWTToken = async () => {
    const response = await fetch('/api/v1/jwt-token');
    return response.json();
};

    onMounted(async () => {
        let token = await getCsrfToken();
        csrf_token.value = token.csrf_token;

        let user_id = await getUserId();
        current_user_id.value = user_id.id;

        let jwt = await getJWTToken();
        jwt_token.value = jwt.jwt_token;

        info.value = true;       
    });


    let makePost = () => {
        let post_form = document.querySelector('#postForm');
        let form_data = new FormData(post_form);
        const alert = document.querySelector("#alert");

        fetch(`/api/v1/users/${current_user_id.value}/posts`, {
            method: 'POST',
            body: form_data,
            headers: {
                'X-CSRFToken': csrf_token.value,
                Authorization: 'Bearer ' + jwt_token.value,
            }
        }).then(function (response) {
            return response.json();
        }).then(function (data) {
            alert.style.display = 'block'
            alert.textContent = data.message ? data.message : data.errors[0]
            router.push('/explore');
        });
    }
</script>

<template>
    <div class="alert" id="alert"></div>
    <form v-if="info" @submit.prevent="makePost" enctype="multipart/form-data" id="postForm">
            <div class="form-group">
                <label for="photo">Photo</label>
                <input type="file" name="photo" class="formcontrol" accept="image/*">
            </div>
            <div class="form-group">
                <label for="caption">Caption</label>
                <input type="text" name="caption" class="formcontrol">
            </div> 
            <div class="form-group">
                <button type="submit" class="btn btn-register">Submit</button>
            </div> 
        </form>
</template>