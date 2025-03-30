package org.example.exam_atlas.Servlet;

import com.google.gson.*;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.*;
import org.example.exam_atlas.Dao.Documentdao;
import org.example.exam_atlas.Model.*;

import java.io.*;
import java.util.List;
import java.util.stream.Collectors;

@WebServlet(name = "DocumentServlet", urlPatterns = {"/documents"})
public class DocumentServlet extends HttpServlet {

    private final Documentdao documentdao = new Documentdao();


    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse res) throws IOException {
        List<Document> documents = documentdao.findAll();
        res.setContentType("application/json");
        new Gson().toJson(documents, res.getWriter());
    }


    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse res) throws IOException {
        String body = req.getReader().lines().collect(Collectors.joining());
        JsonObject json = JsonParser.parseString(body).getAsJsonObject();

        String type = json.get("type").getAsString(); // Ex: "book" ou "magazine"
        Document document = null;

        if ("book".equalsIgnoreCase(type)) {
            document = new Gson().fromJson(json, Book.class);
        } else if ("magazine".equalsIgnoreCase(type)) {
            document = new Gson().fromJson(json, Magazine.class);
        }

        if (document != null) {
            documentdao.create(document);
            res.setContentType("application/json");
            res.getWriter().write("{\"message\": \"Document ajouté avec succès\"}");
        } else {
            res.sendError(HttpServletResponse.SC_BAD_REQUEST, "Type de document invalide (book ou magazine).");
        }
    }
}

