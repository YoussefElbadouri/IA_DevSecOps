package org.example.exam_atlas.Dao;



import jakarta.persistence.EntityManager;
import jakarta.persistence.EntityManagerFactory;
import jakarta.persistence.Persistence;
import org.example.exam_atlas.Model.Borrow;

import java.time.LocalDate;
import java.util.List;

public class Borrowdao {
    public static EntityManagerFactory entityManagerFactory;

    static {
        try {
            entityManagerFactory = Persistence.createEntityManagerFactory("exam");
        } catch (Exception e) {
            System.err.println("Erreur lors de l'initialisation de l'EntityManagerFactory : " + e.getMessage());
            e.printStackTrace();
        }
    }

    public void create(Borrow borrow) {
        EntityManager em = entityManagerFactory.createEntityManager();
        try {
            em.getTransaction().begin();
            em.persist(borrow);
            em.getTransaction().commit();
        } finally {
            em.close();
        }
    }

    public Borrow findById(Long id) {
        EntityManager em = entityManagerFactory.createEntityManager();
        try {
            return em.find(Borrow.class, id);
        } finally {
            em.close();
        }
    }

    public List<Borrow> findAll() {
        EntityManager em = entityManagerFactory.createEntityManager();
        try {
            return em.createQuery("SELECT b FROM Borrow b", Borrow.class).getResultList();
        } finally {
            em.close();
        }
    }

    public List<Borrow> findActiveBorrows() {
        EntityManager em = entityManagerFactory.createEntityManager();
        try {
            return em.createQuery("SELECT b FROM Borrow b WHERE b.returnDate IS NULL", Borrow.class)
                    .getResultList();
        } finally {
            em.close();
        }
    }
    public void markAsReturned(Long borrowId) {
        EntityManager em = entityManagerFactory.createEntityManager();
        try {
            em.getTransaction().begin();
            Borrow borrow = em.find(Borrow.class, borrowId);
            if (borrow != null && borrow.getReturnDate() == null) {
                borrow.setReturnDate(LocalDate.now());
                em.merge(borrow);
            }
            em.getTransaction().commit();
        } finally {
            em.close();
        }
    }


    public void update(Borrow borrow) {
        EntityManager em = entityManagerFactory.createEntityManager();
        try {
            em.getTransaction().begin();
            em.merge(borrow);
            em.getTransaction().commit();
        } finally {
            em.close();
        }
    }

    public void delete(Long id) {
        EntityManager em = entityManagerFactory.createEntityManager();
        try {
            em.getTransaction().begin();
            Borrow borrow = em.find(Borrow.class, id);
            if (borrow != null) {
                em.remove(borrow);
            }
            em.getTransaction().commit();
        } finally {
            em.close();
        }
    }
}
