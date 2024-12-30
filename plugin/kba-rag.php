<?php
/**
 * Plugin Name: KBA Flask RAG Connector
 * Description: Verbindt WordPress met de Flask RAG API.
 * Version: 1.0
 * Author: YininAI
 */

// Voeg een shortcode toe voor de frontend
add_shortcode('rag_interface', 'render_rag_interface');

function render_rag_interface() {
    ob_start();
    ?>
    <div id="rag-interface">
        <h3>Document Upload</h3>
        <input type="file" id="fileUpload" multiple />
        <button id="uploadButton">Upload Bestanden</button>
        <div id="uploadResult"></div>

        <h3>Vraag stellen</h3>
        <input type="text" id="userQuestion" placeholder="Stel een vraag" />
        <button id="askButton">Stel Vraag</button>
        <div id="answerResult"></div>
    </div>
    <?php
    return ob_get_clean();
}
?>



