package org.example.exam_atlas.Servlet;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import jakarta.persistence.EntityManager;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.*;
import org.example.exam_atlas.Dao.Borrowdao;
import org.example.exam_atlas.Model.*;

import java.io.*;
import java.time.LocalDate;
import java.util.List;

@WebServlet(name = "BorrowServlet", urlPatterns = {"/borrow-action"})

public class Borrowservlet extends HttpServlet {

    private final Borrowdao borrowdao = new Borrowdao();


    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse res) throws IOException {
        List<Borrow> borrows = borrowdao.findActiveBorrows();
        res.setContentType("application/json");
        new Gson().toJson(borrows, res.getWriter());
    }


    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse res) throws IOException {
        JsonObject json = JsonParser.parseReader(req.getReader()).getAsJsonObject();
        Long userId = json.get("userId").getAsLong();
        Long documentId = json.get("documentId").getAsLong();

        EntityManager em = Borrowdao.entityManagerFactory.createEntityManager();
        try {
            em.getTransaction().begin();

            User user = em.find(User.class, userId);
            Document document = em.find(Document.class, documentId);

            if (user == null || document == null) {
                res.sendError(HttpServletResponse.SC_NOT_FOUND, "Utilisateur ou Document introuvable.");
                return;
            }

            Borrow borrow = new Borrow();
            borrow.setUser(user);
            borrow.setDocument(document);
            borrow.setDateBorrow(LocalDate.now());

            em.persist(borrow);
            em.getTransaction().commit();

            res.setContentType("application/json");
            res.getWriter().write("{\"message\": \"Emprunt effectué\"}");
        } finally {
            em.close();
        }
    }


    @Override
    protected void doPut(HttpServletRequest req, HttpServletResponse res) throws IOException {
        JsonObject json = JsonParser.parseReader(req.getReader()).getAsJsonObject();
        Long borrowId = json.get("borrowId").getAsLong();

        borrowdao.markAsReturned(borrowId);

        res.setContentType("application/json");
        res.getWriter().write("{\"message\": \"Document retourné\"}");
    }
}
