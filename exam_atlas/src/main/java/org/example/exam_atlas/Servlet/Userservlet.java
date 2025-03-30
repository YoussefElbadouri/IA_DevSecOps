package org.example.exam_atlas.Servlet;

import com.google.gson.Gson;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.*;
import org.example.exam_atlas.Dao.Userdao;
import org.example.exam_atlas.Model.User;

import java.io.*;

@WebServlet(name = "UserSservlet", urlPatterns = {"/user"})
public class Userservlet extends HttpServlet {

    private final Userdao userdao = new Userdao();

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse res) throws IOException {
        BufferedReader reader = req.getReader();
        User user = new Gson().fromJson(reader, User.class);

        userdao.create(user);

        res.setContentType("application/json");
        res.getWriter().write("{\"message\": \"Utilisateur ajouté\"}");
    }
}

