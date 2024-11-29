package com.bangkit.letmecook.ui.usersAuth

import android.content.Intent
import android.os.Bundle
import android.text.SpannableString
import android.text.Spanned
import android.text.TextPaint
import android.text.style.ClickableSpan
import android.text.style.ForegroundColorSpan
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.bangkit.letmecook.MainActivity
import com.bangkit.letmecook.R
import com.bangkit.letmecook.databinding.ActivitySignInBinding
import com.google.firebase.auth.FirebaseAuth

class SignInActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySignInBinding
    private lateinit var firebaseAuth: FirebaseAuth

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySignInBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Inisialisasi Firebase Authentication
        firebaseAuth = FirebaseAuth.getInstance()

        // Tambahkan efek SpannableString untuk teks "Sign Up"
        setupSignUpLink()

        // Tombol Sign In menggunakan Email dan Password
        binding.button.setOnClickListener {
            val email = binding.emailEt.text.toString()
            val password = binding.passET.text.toString()

            if (email.isNotEmpty() && password.isNotEmpty()) {
                signInWithEmail(email, password)
            } else {
                Toast.makeText(this, "Email dan Password tidak boleh kosong!", Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onStart() {
        super.onStart()
        // Jika pengguna sudah masuk, langsung navigasi ke MainActivity
        if (firebaseAuth.currentUser != null) {
            navigateToMain()
        }
    }

    private fun setupSignUpLink() {
        val fullText = "Don't Have Account? Sign Up"
        val spannableString = SpannableString(fullText)

        // Warna khusus untuk kata "Sign Up"
        val colorSpan = ForegroundColorSpan(ContextCompat.getColor(this, R.color.purple_500))
        spannableString.setSpan(colorSpan, 20, 27, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)

        // Membuat kata "Sign Up" dapat diklik
        val clickableSpan = object : ClickableSpan() {
            override fun onClick(widget: View) {
                // Navigasi ke halaman SignUp
                val intent = Intent(this@SignInActivity, SignUpActivity::class.java)
                startActivity(intent)
            }

            override fun updateDrawState(ds: TextPaint) {
                super.updateDrawState(ds)
                ds.isUnderlineText = false // Menonaktifkan garis bawah
            }
        }
        spannableString.setSpan(clickableSpan, 20, 27, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)

        // Pasang SpannableString ke TextView
        binding.textView.text = spannableString
        binding.textView.movementMethod = android.text.method.LinkMovementMethod.getInstance()
        binding.textView.highlightColor = android.graphics.Color.TRANSPARENT
    }

    private fun signInWithEmail(email: String, password: String) {
        firebaseAuth.signInWithEmailAndPassword(email, password).addOnCompleteListener { task ->
            if (task.isSuccessful) {
                navigateToMain()
            } else {
                Toast.makeText(this, task.exception?.message ?: "Sign In gagal", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun navigateToMain() {
        val intent = Intent(this, MainActivity::class.java)
        startActivity(intent)
        finish()
    }
}
