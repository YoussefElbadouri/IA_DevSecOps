package org.example.exam_atlas.Dao;

import jakarta.persistence.EntityManager;
import jakarta.persistence.EntityManagerFactory;
import jakarta.persistence.Persistence;
import org.example.exam_atlas.Model.Document;

import java.util.List;

public class Documentdao {
    public static EntityManagerFactory entityManagerFactory;
    static {
        try {
            entityManagerFactory = Persistence.createEntityManagerFactory("exam");
        } catch (Exception e) {
            System.err.println("Erreur lors de l'initialisation de l'EntityManagerFactory : " + e.getMessage());
            e.printStackTrace();
        }
    }

    public void create(Document document) {
        EntityManager em = entityManagerFactory.createEntityManager();
        try {
            em.getTransaction().begin();
            em.persist(document);
            em.getTransaction().commit();
        } finally {
            em.close();
        }
    }

    public Document findById(Long id) {
        EntityManager em = entityManagerFactory.createEntityManager();
        try {
            return em.find(Document.class, id);
        } finally {
            em.close();
        }
    }

    public List<Document> findAll() {
        EntityManager em = entityManagerFactory.createEntityManager();
        try {
            return em.createQuery("SELECT d FROM Document d", Document.class).getResultList();
        } finally {
            em.close();
        }
    }
    public void update(Document document) {
        EntityManager em = entityManagerFactory.createEntityManager();
        try {
            em.getTransaction().begin();
            em.merge(document);
            em.getTransaction().commit();
        } finally {
            em.close();
        }
    }

    public void delete(Long id) {
        EntityManager em = entityManagerFactory.createEntityManager();
        try {
            em.getTransaction().begin();
            Document doc = em.find(Document.class, id);
            if (doc != null) {
                em.remove(doc);
            }
            em.getTransaction().commit();
        } finally {
            em.close();
        }
    }
}
