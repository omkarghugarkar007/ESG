// Word cloud logic
document.addEventListener('DOMContentLoaded', function () {
    // Sample data for the word cloud
    var paragraph = "Technology is the study of scientific knowledge in order to create tools and processes that may be used to change the world by increasing efficiency in nearly every aspect of our lives. Technology has made our lives easier, and all human beings have become entirely dependent on technology.";
  
    // Extract words from the paragraph
    var words = paragraph.split(/\s+/).map(function(word) {
      return { text: word, size: Math.random() * 40 + 10 };
    });
  
    // Set up the layout options
    var width = 800;
    var height = 400;
  
    // Create the word cloud layout
    var layout = d3.layout.cloud()
      .size([width, height])
      .words(words)
      .padding(5)
      .rotate(function() { return ~~(Math.random() * 2) * 90; })
      .fontSize(function(d) { return d.size; })
      .on('end', draw);
  
    // Generate the word cloud
    layout.start();
  
    // Function to draw the word cloud
    function draw(words) {
      d3.select('#wordcloud').append('svg')
        .attr('width', width)
        .attr('height', height)
        .append('g')
        .attr('transform', 'translate(' + width / 2 + ',' + height / 2 + ')')
        .selectAll('text')
        .data(words)
        .enter().append('text')
        .attr('class', 'word') // Add the 'word' class for the hover effect
        .style('font-size', function(d) { return d.size + 'px'; })
        .style('fill', '#4b4276')
        .attr('text-anchor', 'middle')
        .attr('transform', function(d) {
          return 'translate(' + [d.x, d.y] + ')rotate(' + d.rotate + ')';
        })
        .text(function(d) { return d.text; });
    }
  });