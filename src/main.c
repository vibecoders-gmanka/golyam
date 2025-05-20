#include <gtk/gtk.h>
#include <adwaita.h>

// Function to be called when the application is activated
static void
activate (GtkApplication *app, gpointer user_data) {
  // Get the AdwApplication from GtkApplication
  AdwApplication *adw_app = ADW_APPLICATION (app);

  // Create a new AdwApplicationWindow
  GtkWidget *window = adw_application_window_new (adw_app);
  gtk_window_set_title (GTK_WINDOW (window), "Hello World");
  gtk_window_set_default_size (GTK_WINDOW (window), 200, 100);

  // Create a GtkLabel with "Hello World"
  GtkWidget *label = gtk_label_new ("Hello World");

  // Set the label as the child of the window
  gtk_window_set_child (GTK_WINDOW (window), label);

  // Present the window
  gtk_window_present (GTK_WINDOW (window));
}

// Main function
int
main (int argc, char **argv) {
  // Define the application ID
  const char *app_id = "com.example.HelloWorld";

  // Create an AdwApplication instance
  AdwApplication *app = adw_application_new (app_id, G_APPLICATION_FLAGS_NONE);

  // Connect the "activate" signal to the activate function
  g_signal_connect (app, "activate", G_CALLBACK (activate), NULL);

  // Run the application
  int status = g_application_run (G_APPLICATION (app), argc, argv);

  // Release the application object
  g_object_unref (app);

  return status;
}
