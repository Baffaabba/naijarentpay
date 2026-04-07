from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message
from .forms import MessageForm


@login_required
def messages_list(request):
    user = request.user
    if user.is_tenant:
        conversations = Conversation.objects.filter(
            tenant=user
        ).select_related("landlord", "rental_property").prefetch_related("messages").order_by("-created_at")
    else:
        conversations = Conversation.objects.filter(
            landlord=user
        ).select_related("tenant", "rental_property").prefetch_related("messages").order_by("-created_at")

    active_id = request.GET.get("conv")
    active_conv = None
    if active_id:
        active_conv = conversations.filter(pk=active_id).first()
        if active_conv:
            active_conv.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)

    form = MessageForm()
    chat_messages = active_conv.messages.all().select_related("sender") if active_conv else []
    return render(request, "messaging/messages.html", {
        "conversations": conversations,
        "active_conv": active_conv,
        "chat_messages": chat_messages,
        "form": form,
    })


@login_required
def send_message(request, conv_id):
    conv = get_object_or_404(Conversation, pk=conv_id)
    if request.user not in [conv.tenant, conv.landlord]:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = Message.objects.create(
                conversation=conv,
                sender=request.user,
                content=form.cleaned_data["content"],
            )
            if request.htmx:
                return render(request, "partials/message_bubble.html", {"message": msg})
            return redirect(f"/messages/?conv={conv_id}")
    return redirect(f"/messages/?conv={conv_id}")


@login_required
def initiate_conversation(request, property_pk):
    from properties.models import Property
    from django.http import HttpResponseForbidden
    prop = get_object_or_404(Property, pk=property_pk)
    if prop.landlord == request.user:
        return HttpResponseForbidden("You cannot message yourself.")
    conv, _ = Conversation.objects.get_or_create(
        tenant=request.user,
        landlord=prop.landlord,
        rental_property=prop,
    )
    return redirect(f"/messages/?conv={conv.pk}")
