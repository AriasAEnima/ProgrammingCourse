const requestOptions = {
  method: "GET",
  redirect: "follow"
};

fetch("https://http.cat/status/100", requestOptions)
  .then((response) => response.text())
  .then((result) => console.log(result))
  .catch((error) => console.error(error));