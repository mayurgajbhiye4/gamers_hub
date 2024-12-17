const searchResults = document.getElementById('searchResults');

      if (searchResults.length == 0){
        searchResults.classList.add('d-none');
      }
      else{
        searchResults.classList.remove('d-none');
      }