<script setup>
    import { ref, onMounted } from "vue";
    import router from "../router/index";

    let csrf_token = ref("");

    let info = ref(false);

    let getCsrfToken = async () => {
    const response = await fetch('/api/v1/csrf-token');
    return response.json();
};

    onMounted(async () => {
        let token = await getCsrfToken();
        csrf_token.value = token.csrf_token;

        info.value = true;
    });
    
    let registerUser = () => {
        let registerForm = document.querySelector('#registerForm');
        let form_data = new FormData(registerForm);
        const alert = document.querySelector("#alert");

        fetch('/api/v1/register', {
            method: 'POST',
            body: form_data,
            headers: {
                'X-CSRFToken': csrf_token.value,
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
    <form v-if="info" @submit.prevent="registerUser" enctype="multipart/form-data" id="registerForm">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" name="username" class="formcontrol">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" name="password" class="formcontrol">
            </div>
            <div class="form-group">
                <label for="first_name">First Name</label>
                <input type="text" name="first_name" class="formcontrol">
            </div>
            <div class="form-group">
                <label for="last_name">Last Name</label>
                <input type="text" name="last_name" class="formcontrol">
            </div>
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" name="email" class="formcontrol">
            </div>
            <div class="form-group">
                <label for="location">Location</label>
                <input type="text" name="location" class="formcontrol">
            </div>
            <div class="form-group">
                <label for="bio">Biography</label>
                <input type="text" name="bio" class="formcontrol">
            </div>
            <div class="form-group">
                <label for="photo">Photo</label>
                <input type="file" name="photo" class="formcontrol" accept="image/*">
            </div>
            <div class="form-group">
                <button type="submit" class="btn btn-register">Register</button>
            </div>
    </form>
</template>