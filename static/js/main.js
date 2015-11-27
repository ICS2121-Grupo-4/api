$(document).ready(function() {
    var pool = [1, 10, 19, 145, 153, 2628, 296, 356, 364, 367, 502, 519, 588, 589, 673, 778, 780, 912, 1036, 1101],
        movies_rated = [],
        ratings = [],
        buildRequestUrl = function() {
            // /predict?movies=1&ratings=5
            var baseUrl = "/predict?movies=";
            baseUrl += movies_rated.join(",");
            baseUrl += "&ratings=";
            baseUrl += ratings.join(",");
            
            return baseUrl;
        },
        handlePredictions = function(data) {
            var target = $(".peliculas_predichas").find(".row");
            target.empty();

            loadRandomMovie();

            for (var movie_id in data) {
                if (data.hasOwnProperty(movie_id)) {
                    var div = $("<div />").addClass("col-md-3"),
                        poster = $("<img />").attr("src", data[movie_id].image),
                        title = $("<p />").text(data[movie_id].title),
                        score = $("<p />").text(data[movie_id].score);
                    poster.appendTo(div);
                    title.appendTo(div);
                    score.appendTo(div);
                    div.appendTo(target);
                }
            }
        },
        loadRandomMovie = function() {
            var rand = Math.random(),
                index = Math.floor(rand * pool.length),
                movie_id = pool[index],
                target = $("#image-container");
            target.empty();
            pool.splice(index, 1);
            $.ajax({
                url: "movie_info",
                data: {movie_id: movie_id},
                success: function(data) {
                    var poster = $("<img />").attr("src", data.image),
                        title = $("<p />").text(data.title);
                    poster.appendTo(target);
                    title.appendTo(target);
                    $("#image-container").data("current-movie-id", data.movie_id);
                }
            });
        };

    loadRandomMovie();

    // Escuchar clicks en botones
    $("#like").click(function(ev) {
        movies_rated.push($("#image-container").data("current-movie-id"));
        ratings.push(5);

        $.ajax({
            url: buildRequestUrl(),
            success: function(data) {
                handlePredictions(data);
            }
        });

        ev.preventDefault();
    });

    $("#dislike").click(function(ev) {
        movies_rated.push($("#image-container").data("current-movie-id"));
        ratings.push(-5);

        $.ajax({
            url: buildRequestUrl(),
            success: function(data) {
                handlePredictions(data);
            }
        });
        ev.preventDefault();
    });
});
